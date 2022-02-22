from audioop import reverse

from accounts.models import Managers, Tenants
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponse, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rental_property.models import Building, RentalUnit

from core.forms import ContactForm, UnitTourForm, VisitUpdateForm, EvictionNoticeForm
from core.models import Contact, UnitTour


def home(request):
    return render(request, 'core/home.html')

class CreateContact(SuccessMessageMixin, CreateView):
    model = Contact
    form_class = ContactForm
    success_message = "Your contact has been submitted."
    success_url = reverse_lazy('operational-buildings')

def schedule_unit_tour(request, unit_slug):
    unit = RentalUnit.objects.get(slug=unit_slug)

    if request.method == 'POST':
        tour_form = UnitTourForm(request.POST)
        if tour_form.is_valid():
            tour_form.instance.unit = unit
            tour_form.save()
            # add sending email by template.
            messages.success(request, 'Visit has been added, check email for confirmation.')
            return redirect('unit-details', building_slug=unit.building.slug, unit_slug=unit.slug)
    else:
        tour_form = UnitTourForm()
    context = {'unit': unit, 'tour_form': tour_form}
    return render(request, 'core/tour-unit.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def scheduled_visits(request, building_slug):
    building = Building.objects.get(slug=building_slug)

    get_by = request.GET.get('filter', 'waiting')

    if get_by == 'waiting':
        visits = UnitTour.objects.filter(unit__building=building, visit_status='waiting')
    elif get_by == 'cancelled':
        visits = UnitTour.objects.filter(unit__building=building, visit_status='cancelled')
    elif get_by == 'visited':
        visits = UnitTour.objects.filter(unit__building=building, visit_status='visited')
    elif get_by == 'approved':
        visits = UnitTour.objects.filter(unit__building=building, visit_status='approved')
    else:
        visits = UnitTour.objects.filter(unit__building=building)

    context = {'building':building, 'visits':visits}
    return render(request, 'core/vists.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_view_visits(request, building_slug, visit_code):
    building = Building.objects.get(slug=building_slug)
    visit = UnitTour.objects.get(visit_code=visit_code, unit__building=building)

    last_updater = Managers.objects.get(associated_account=request.user)

    if request.method == 'POST':
        update_visit_form = VisitUpdateForm(request.POST, instance=visit)
        if update_visit_form.is_valid():
            update_visit_form.instance.last_updated_by = last_updater
            update_visit_form.save()
            messages.success(request, 'Visit was updated successfully')
            return redirect('visits', building_slug=building.slug)
            # TODO: Add send email if visit is Approved
    else:
        update_visit_form = VisitUpdateForm(instance=visit)
    context = {'visit':visit, 'update_visit_form': update_visit_form}
    return render(request, 'core/visits-update.html', context)


@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def eviction_notice(request, building_slug, unit_slug, username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building, slug=unit_slug)
    manager = Managers.objects.get(associated_account__username=request.user.username)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)

    if request.method == 'POST':
        eviction_form = EvictionNoticeForm(request.POST)
        if eviction_form.is_valid():
            eviction_form.instance.sent_by = manager
            eviction_form.instance.tenant = tenant
            eviction_form.instance.unit = unit
            eviction_form.save()
            # TODO: add email notification
            messages.success(request, 'Eviction notice has een sent!')
            return redirect('view-tenant', building_slug=building.slug, username=tenant.associated_account.username)
    else:
        eviction_form = EvictionNoticeForm()
    
    context = {'eviction_form':eviction_form, 'tenant':tenant, 'unit': unit}
    return render(request, 'core/eviction-notice.html', context)