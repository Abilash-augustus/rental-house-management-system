from accounts.models import Tenants
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from rental_property.models import Building, RentalUnit
from django.forms import modelformset_factory
from complaints.forms import UnitReportAlbumForm, UnitReportForm
from complaints.models import Complaints, UnitReport, UnitReportAlbum, UnitReportType
from django.contrib import messages

User = get_user_model()


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
def view_reports(request, building_slug):
    building = Building.objects.get(slug=building_slug)

    status = request.GET.get('status', 'received')

    if status == 'received':
        reports = UnitReport.objects.filter(unit__building=building, status='rc')
    elif status == 'processing':
        reports = UnitReport.objects.filter(unit__building=building, status='pr')
    elif status == 'caancelled':
        reports = UnitReport.objects.filter(unit__building=building, status='dr')
    elif status == 'resolved':
        reports = UnitReport.objects.filter(unit__building=building, status='rs')

    context = {'reports': reports, 'building': building,}
    return render(request, 'complaints/reports-by-building.html', context)