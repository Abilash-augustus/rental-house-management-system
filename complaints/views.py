from django.http import HttpResponse, JsonResponse
from accounts.models import Tenants
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from rental_property.models import Building, RentalUnit

from complaints.filters import ComplaintsFilter, UnitReportFilter
from complaints.forms import (NewComplaintForm, ReportUpdateForm,
                              UnitReportAlbumForm, UnitReportForm,
                              UpdateComplaintForm)
from complaints.models import (Complaints, UnitReport, UnitReportAlbum,
                               UnitReportType)

User = get_user_model()

#interacting with tenant reports
@login_required
def create_a_report(request, unit_slug, username):
    unit = RentalUnit.objects.get(slug=unit_slug)
    user_instance = User.objects.get(username=username)
    tenant_instance = Tenants.objects.get(associated_account_id=user_instance)
    image_form_set = modelformset_factory(
        UnitReportAlbum, form=UnitReportAlbumForm, extra=5)

    if request.method == 'POST':
        report_form = UnitReportForm(request.POST)
        formset = image_form_set(
            request.POST, request.FILES, queryset=UnitReportAlbum.objects.none())

        if report_form.is_valid() and formset.is_valid():
            reportform = report_form.save(commit=False)
            reportform.reported_by = tenant_instance
            reportform.unit = unit
            reportform.save()

            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    photo = UnitReportAlbum(
                        unit_report=reportform, image=image)
                    photo.save()
            # TODO: Add email notification to render template
            messages.success(request, 'Your report has been submitted!')
            return redirect('profile')
        else:
            print(report_form.errors, formset.errors)
    else:
        report_form = UnitReportForm()
        formset = image_form_set(queryset=UnitReportAlbum.objects.none())
    context = {'report_form': report_form, 'formset': formset}
    return render(request, 'complaints/make-report.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='available-units')
def view_reports(request, building_slug):
    building = Building.objects.get(slug=building_slug)

    reports = UnitReport.objects.filter(unit__building=building)
    reports_filter = UnitReportFilter(request.GET, queryset=reports)
    
    context = {'reports':reports_filter, 'building': building,}
    return render(request, 'complaints/reports-by-building.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_reports(request, building_slug, unit_slug, report_code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building, slug=unit_slug)
    report = UnitReport.objects.get(unit=unit, code=report_code)
    images = UnitReportAlbum.objects.filter(unit_report=report)
    
    if request.method == 'POST':
        update_form = ReportUpdateForm(request.POST, instance=report)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, 'Report updated successfully!')
            return redirect('reports', building_slug=building.slug)
    else:
        update_form = ReportUpdateForm(instance=report)
    
    context = {'building':building, 'report':report, 'update_form':update_form, 'images':images}
    return render(request, 'complaints/report-update.html', context)

# TODO: needs correction not posting
@login_required
def create_complaint(request, building_slug):
    building = Building.objects.get(slug=building_slug)
        
    if request.method == 'POST':
        complaint_form = NewComplaintForm(request.POST)
        if complaint_form.is_valid():
            complaint_form.instance.building = building
            complaint_form.save()
            messages.success(request, 'Complaint posted')
            return redirect('profile')
    else:
        complaint_form = NewComplaintForm()
    context = {'complaint_form':complaint_form}
    return render(request, 'complaints/create-complaint.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def building_complaints(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    
    complaints = Complaints.objects.filter(building=building)
    complaint_filter = ComplaintsFilter(request.GET, queryset=complaints)
    
    context = {'complaints':complaint_filter, 'building':building}
    return render(request, 'complaints/complaints.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def complaint_update(request, building_slug, complaint_code):
    building = Building.objects.get(slug=building_slug)
    complaint = Complaints.objects.get(building=building,complaint_code=complaint_code)
    
    if request.method == 'POST':
        update_form = UpdateComplaintForm(request.POST, instance=complaint)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, 'Complaint status updates')
            return redirect('building-complaints', building_slug=building.slug)
    else:
        update_form = UpdateComplaintForm(instance=complaint)
    context = {'building':building, 'update_form':update_form, 'complaint':complaint}
    return render(request, 'complaints/complaint_update.html', context)

@login_required
def reports_overview(request,building_slug):
    building = Building.objects.get(slug=building_slug)
    
    labels = []
    data = []
    
    queryset = UnitReport.objects.filter(unit__building=building).values(
        'report_type__name').annotate(count=Count('pk'))
    
    for entry in queryset:
        labels.append(entry['report_type__name'])
        data.append(entry['count'])
    
    data = {'labels': labels,'data': data}
    return JsonResponse(data)

@login_required
def complaints_overview(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    
    labels = []
    data = []
    
    queryset = Complaints.objects.filter(building=building).values(
        'status').annotate(count=Count('status'))
    
    for entry in queryset:
        labels.append(entry['status'])
        data.append(entry['count'])
    
    data = {'labels': labels,'data': data}
    return JsonResponse(data)