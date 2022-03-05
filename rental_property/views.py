from itertools import chain
from django.db.models import Count
from django.http import JsonResponse
from accounts.models import Tenants
from complaints.models import UnitReport
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import InvalidPage, PageNotAnInteger, Paginator
from django.forms import modelformset_factory
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)

from rental_property.forms import (AddRentalUnitForm, BuildingUpdateForm,
                                   UnitAlbumForm, UpdateRentalUnit)
from rental_property.models import (Building, Counties, Estate, RentalUnit,
                                    UnitAlbum, UnitType)
from rental_property.filters import UnitsFilter,TenantsFilter


def property_by_county(request, county_slug):
    if county_slug != None:
        county_page = get_object_or_404(Counties, slug=county_slug)
        building_list = Building.objects.filter(county=county_page, building_status='op')
    else:
        building_list = Building.objects.filter(building_status='op')

    paginator = Paginator(list(chain(building_list)), 2)
    try:
        page = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        page = 1
    try:
        buildings = paginator.page(page)
    except InvalidPage:
        buildings = paginator.page(paginator.num_pages)
    
    context = {'county': county_page, 'buildings':buildings,}
    return render(request, 'rental_property/list-by-county.html', context)

def buildings(request):
    operational_buildings = Building.objects.filter(building_status='op')
    context = {'operational_buildings':operational_buildings,}
    return render(request, 'rental_property/available_buildings.html', context)

def open_building_units(request, building_slug):
    building = get_object_or_404(Building, slug=building_slug)
    rental_units = RentalUnit.objects.filter(building=building, status='ready')
    unit_count = rental_units.count()
    context = {'unit_count': unit_count, 'rental_units':rental_units, 'building': building}
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
    total_units = units.count()
        
    context = {'units':units_filter,'total_units':total_units, 'building':building,}
    return render(request, 'rental_property/managed_building_units.html', context)
    
# TODO: filter buildings to a specific area

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
            return redirect('building-units', building_slug=building.slug)
        else:
            print(unit_form.errors, formset.errors)
    else:
        unit_form = AddRentalUnitForm()
        formset = image_form_set(queryset=UnitAlbum.objects.none())
    context = {'unit_form':unit_form, 'formset':formset}
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
    