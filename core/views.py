from audioop import reverse

from accounts.models import Managers, Tenants
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponse, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rental_property.models import Building, RentalUnit

from core.forms import ContactForm, UnitTourForm
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
    else:
        visits = UnitTour.objects.filter(unit__building=building)

    context = {'building':building, 'visits':visits}
    return render(request, 'core/vists.html', context)
