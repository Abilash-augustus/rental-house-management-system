from audioop import reverse

from accounts.models import Managers, Tenants
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rental_property.models import Building, RentalUnit

from core.forms import (CancelMoveOutForm, ContactForm, EvictionNoticeForm,
                        NewVacateNoticeForm, UnitTourForm, UpdateVacateNotice,
                        VisitUpdateForm)
from core.models import Contact, EvictionNotice, UnitTour, VacateNotice

User = get_user_model()


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
def create_eviction_notice(request, building_slug, unit_slug, username):
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
            messages.success(request, 'Eviction notice has been sent!')
            return redirect('view-tenant', building_slug=building.slug, username=tenant.associated_account.username)
    else:
        eviction_form = EvictionNoticeForm()
    
    context = {'eviction_form':eviction_form, 'tenant':tenant, 'unit': unit}
    return render(request, 'core/create-eviction-notice.html', context)


@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def view_eviction_notices(request,building_slug):
    building = Building.objects.get(slug=building_slug)
    
    get_by_status = request.GET.get('status', 'in-progress')
    
    if get_by_status == 'in-progress':
        notices = EvictionNotice.objects.filter(unit__building=building, eviction_status='initiated')
    elif get_by_status == 'dropped':
        notices = EvictionNotice.objects.filter(unit__building=building, eviction_status='dropped')
    elif get_by_status == 'evicted':
        notices = EvictionNotice.objects.filter(unit__building=building, eviction_status='evicted')
    else:
        notices = EvictionNotice.objects.filter(unit__building=building)
    
    context = {'notices':notices, 'building':building, 'get_by_status':get_by_status}
    return render(request, 'core/view-eviction-notices.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def eviction_notice_display(request,building_slug, notice_code):
    building = Building.objects.get(slug=building_slug)
    notice = EvictionNotice.objects.get(unit__building=building, notice_code=notice_code)
    context = {'building':building, 'notice':notice}
    return render(request, 'core/e-notice-display.html', context)
#evictipn notice display for users
    
@login_required
@user_passes_test(lambda user: user.is_tenant==True, login_url='profile')
def my_notice_to_vacate(request, building_slug, username):
    building = Building.objects.get(slug=building_slug)
    user_instance = User.objects.get(username=username)
    tenant = Tenants.objects.get(associated_account=user_instance, rented_unit__building=building)
    
    check_if_notice_exists = VacateNotice.objects.filter(tenant=tenant,notice_status='received')
    if check_if_notice_exists:
        messages.success(request, 'You already have a notice in place')
        messages.info(request, 'Operation not allowed')
        return redirect('profile')
    else:
        if request.method == 'POST':
            vacate_form = NewVacateNoticeForm(request.POST)
            if vacate_form.is_valid():
                vacate_form.instance.tenant = tenant
                vacate_form.save()
                messages.success(request, 'Your notice has been received')
                return redirect('profile')
        else:
            vacate_form = NewVacateNoticeForm()
        
    context = {'vacate_form':vacate_form, 'building':building, 'tenant':tenant,
               'check_if_notice_exists':check_if_notice_exists}
    return render(request, 'core/my_vacate_notice.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def vacate_notice_update(request, building_slug, notice_code):
    building = Building.objects.get(slug=building_slug)
    notice = VacateNotice.objects.get(tenant__rented_unit__building=building, code=notice_code)
    
    if request.method == 'POST':
        v_update_form = UpdateVacateNotice(request.POST, instance=notice)
        if v_update_form.is_valid():
            v_update_form.save()
            messages.success(request, 'Status changed')
            return redirect('core:move-out-notices', building_slug=building.slug)
    else:
        v_update_form = UpdateVacateNotice(instance=notice)
    context = {'v_update_form':v_update_form,'notice':notice}
    return render(request, 'core/vacate-notice-update.html', context)

@login_required
@user_passes_test(lambda user: user.is_tenant==True, login_url='profile')
def cancel_vacate_notice(request, building_slug, notice_code, username):
    building = Building.objects.get(slug=building_slug)
    user_instance = User.objects.get(username=username)
    tenant = Tenants.objects.get(associated_account=user_instance, rented_unit__building=building)
    notice_instance = VacateNotice.objects.get(tenant=tenant, code=notice_code)
    
    if request.method == 'POST':
        cancel_form = CancelMoveOutForm(request.POST, instance=notice_instance)
        if cancel_form.is_valid():
            cancel_form.save()
            VacateNotice.objects.filter(tenant=tenant).update(notice_status='dropped')
            messages.success(request, 'Your notice has been updated')
            return redirect('profile')
    else:
        cancel_form = CancelMoveOutForm(instance=notice_instance)
        
    context = {'cancel_form':cancel_form, 'building':building, 'tenant':tenant,
               'notice_instance':notice_instance}
    return render(request, 'core/cancel-notice.html', context)

@login_required
@user_passes_test(lambda user: user.is_tenant==True, login_url='profile')
def move_out_notices(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    notice_status = request.GET.get('notice_status', '')
    
    if notice_status == 'received':
        move_out_notices = VacateNotice.objects.filter(tenant__rented_unit__building=building, notice_status='received')
    elif notice_status == 'dropped':
        move_out_notices = VacateNotice.objects.filter(tenant__rented_unit__building=building, notice_status='dropped')
    elif notice_status == 'confirmed':
        move_out_notices = VacateNotice.objects.filter(tenant__rented_unit__building=building, notice_status='confirmed')
    elif notice_status == 'checking':
        move_out_notices = VacateNotice.objects.filter(tenant__rented_unit__building=building, notice_status='checking')
    else:
        move_out_notices = VacateNotice.objects.filter(tenant__rented_unit__building=building)
        
    context = {'move_out_notices':move_out_notices, 'building':building}
    return render(request, 'core/move-out-notices.html', context)

@login_required
def view_move_out_notice(request, building_slug, username, notice_code):
    building = Building.objects.get(slug=building_slug)
    tenant = Tenants.objects.get(associated_account__username=username)
    active_user = request.user
    
    if active_user.is_manager or tenant:
        notice = VacateNotice.objects.get(tenant=tenant,code=notice_code)
    else:
        return redirect('profile')
    context = {'notice':notice,'building':building,'tenant':tenant}
    return render(request, 'core/move-out-notice.html', context)
