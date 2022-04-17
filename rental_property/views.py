from itertools import chain
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from accounts.models import Managers, Tenants
from complaints.models import UnitReport
from django.contrib import messages
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import InvalidPage, PageNotAnInteger, Paginator
from django.forms import modelformset_factory
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.template.loader import get_template
from rental_property.forms import (AddRentalUnitForm, BuildingUpdateForm, NewMaintananceNoticeForm,
                                   UnitAlbumForm, UpdateMaintainanceNotice, UpdateRentalUnit)
from rental_property.models import (Building, Counties, Estate, RentalUnit,
                                    UnitAlbum, UnitType,MaintananceNotice)
from rental_property.filters import BuildingUpdateFilter, MaintananceNoticeFilter, UnitsFilter,TenantsFilter, UserUnitsFilter
from core.utils import render_to_pdf
from config.settings import DEFAULT_FROM_EMAIL
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def buildings(request):
    operational_buildings = Building.objects.filter(building_status='op')
    buildings_filter = BuildingUpdateFilter(request.GET, queryset=operational_buildings)
    
    context = {'operational_buildings':buildings_filter,}
    return render(request, 'rental_property/available_buildings.html', context)

def vacant_building_units(request, building_slug):
    building = get_object_or_404(Building, slug=building_slug)
    rental_units = RentalUnit.objects.filter(building=building, status='ready').order_by('-added')
    rental_units_filter = UserUnitsFilter(request.GET,queryset=rental_units)
    unit_count = rental_units.count()
    context = {'unit_count': unit_count, 'rental_units':rental_units_filter, 'building': building}
    return render(request, 'rental_property/building-units.html', context)


def unit_details(request, building_slug, unit_slug):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building, slug=unit_slug)
    image_album = UnitAlbum.objects.filter(unit=unit)

    context = {
        'building': building, 
        'unit': unit,
        'image_album': image_album,
        }
    return render(request, 'rental_property/unit_details.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def building_dashboard(request, building_slug):

    building = Building.objects.get(slug=building_slug)
        
    building_reports_count = UnitReport.objects.filter(unit__building=building).count()
    
    get_tenants_with_status = request.GET.get('status', 'current-tenants')
    
    tenants = Tenants.objects.filter(moved_in=True, rented_unit__building=building)
    tenants_filter = TenantsFilter(request.GET,queryset=tenants)

    active_tenants_count = Tenants.objects.filter(moved_in=True, rented_unit__building=building).count()
    waiting_tenants_count = Tenants.objects.filter(moved_in=False, rented_unit__building=building).count()

    oc_units_count = RentalUnit.objects.filter(status='occupied', building=building).count() # Number of occupied units
    em_units_count = RentalUnit.objects.filter(status='ready', building=building).count() # Number of unoccupied units
    

    context = {
        'building': building, 'tenants': tenants_filter, 'active_tenants_count':active_tenants_count,
        'waiting_tenants_count':waiting_tenants_count,'oc_units_count':oc_units_count, 'em_units_count':em_units_count,
        'building_reports_count':building_reports_count, 'get_tenants_with_status':get_tenants_with_status}
    return render(request, 'rental_property/managed-building-dashboard.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def managed_building_units(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    
    units = RentalUnit.objects.filter(building=building)
    units_filter = UnitsFilter(request.GET, queryset=units)
    filter_form = units_filter.form
    units_filter = units_filter.qs
    
    paginator = Paginator(units_filter, 9)
    page = request.GET.get('page')
    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)
    total_units = units.count()
        
    context = {'units':response,'total_units':total_units, 'filter_form':filter_form, 'building':building,}
    return render(request, 'rental_property/managed_building_units.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_building_status(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    if request.method == 'POST':
        update_form = BuildingUpdateForm(request.POST, instance=building)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, 'Building Status update successfully')
            return redirect('building-dashboard', building_slug=building.slug)
    else:
        update_form = BuildingUpdateForm(instance=building)
    context = {'update_form':update_form,'building':building}
    return render(request, 'rental_property/update-building-status.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='available-units')
def add_rental_unit(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    image_form_set = modelformset_factory(UnitAlbum, form=UnitAlbumForm, extra=4)

    if request.method == 'POST':
        unit_form = AddRentalUnitForm(request.POST, request.FILES)
        formset = image_form_set(request.POST, request.FILES, queryset=UnitAlbum.objects.none())

        if unit_form.is_valid() and formset.is_valid():
            unitform = unit_form.save(commit=False)
            unitform.added_by = request.user
            unitform.building = building
            unitform.save()

            for form in formset.cleaned_data:
                if form:
                    image =form['image']
                    photo = UnitAlbum(unit=unitform, image=image)
                    photo.save()
            messages.success(request, 'Rental unit was added successfuly!')
            return redirect('managed_building_units', building_slug=building.slug)
        else:
            print(unit_form.errors, formset.errors)
    else:
        unit_form = AddRentalUnitForm()
        formset = image_form_set(queryset=UnitAlbum.objects.none())
    context = {'unit_form':unit_form, 'formset':formset,'building':building}
    return render(request, 'rental_property/add-rental-unit.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_unit(request, building_slug, unit_slug):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building, slug=unit_slug)
    
    if request.method == 'POST':
        unit_update_form = UpdateRentalUnit(request.POST, instance=unit)
        
        if unit_update_form.is_valid():
            unit_update_form.save()
            messages.success(request, 'Unit updated')
            return redirect('managed-building-units', building_slug=building.slug)
    else:
        unit_update_form = UpdateRentalUnit(instance=unit)
    
    context = {'unit_update_form':unit_update_form,'unit':unit,'building':building}
    return render(request, 'rental_property/update-unit.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def property_maintanance_notice(request,building_slug):
    building = Building.objects.get(slug=building_slug)
    tenants = Tenants.objects.filter(rented_unit__building=building)
    
    email_receivers = []
    for tenant in tenants:
        email_receivers.append(tenant.associated_account.email)
    
    get_user = request.user
    if get_user.is_manager:
        manager = Managers.objects.get(associated_account=get_user)
    else:
        return redirect('profile')
    
    if request.method == 'POST':
        new_m_form = NewMaintananceNoticeForm(request.POST)
        if new_m_form.is_valid():
            new_m_form.instance.building = building
            new_m_form.instance.notice_by = manager
            new_m_form.save()
            notify = new_m_form.instance
            if notify.send_email:
                subject = '{0}'.format(notify.title)
                notify_content = 'rental_property/mails/maintanance_notify.html'
                html_message = render_to_string(notify_content,
                                                {'building':building,'notify':notify,})
                from_email = DEFAULT_FROM_EMAIL
                to_email = email_receivers
                message = EmailMessage(subject, html_message, from_email, to_email)
                message.content_subtype = 'html'
                message.send()
                messages.info(request,'Tenants will be notified')
            messages.success(request,'Maintanance notice added')
            return redirect('maintanance_notices', building_slug=building.slug)#change to go to notices
    else:
        new_m_form = NewMaintananceNoticeForm()
    context = {'form': new_m_form, 'building':building,}
    return render(request, 'rental_property/new_maintanance_notice.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def maintanance_notices(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    m_notices = MaintananceNotice.objects.filter(building=building).order_by('-created')
    m_notices_filters = MaintananceNoticeFilter(request.GET, queryset=m_notices)
    context = {'building':building,'notices': m_notices_filters,}
    return render(request, 'rental_property/maintanance_notices.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_maintanance_notice(request, building_slug, ref_number):
    building = Building.objects.get(slug=building_slug)
    notice = MaintananceNotice.objects.get(building=building,ref_number=ref_number)
    
    if request.method == 'POST':
        update_form = UpdateMaintainanceNotice(request.POST,instance=notice)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, 'notice updated')
            return redirect('maintanance_notices', building_slug=building.slug)
    else:
        update_form = UpdateMaintainanceNotice(instance=notice)
    context = {'form': update_form, 'building':building,}
    return render(request, 'rental_property/update_maintanance_notice.html', context)

@login_required
def view_maintanance_notice_pdf(request, building_slug, ref_number):
    building = Building.objects.get(slug=building_slug)
    notice = MaintananceNotice.objects.get(building=building,ref_number=ref_number)
    
    context = {'notice':notice,'building':building}
    template = get_template('pdf/maintanance_notice.html')
    html = template.render(context)
    pdf = render_to_pdf('pdf/maintanance_notice.html', context)
    if pdf:
        response = HttpResponse(pdf,content_type='application/pdf')
        filename = "maintanance_notice_%s" %(notice.ref_number)
        content = "inline; filename='%s'" %(filename)
        download = request.GET.get('download')
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not Found")

@login_required
def units_overview(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    
    labels = []
    data = []
    
    queryset = RentalUnit.objects.filter(building=building).values(
        'status').annotate(count=Count('status'))
    
    for entry in queryset:
        labels.append(entry['status'])
        data.append(entry['count'])
    
    data = {'labels': labels,'data': data}
    return JsonResponse(data)
    