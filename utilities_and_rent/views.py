import datetime

from accounts.models import Managers, Tenants
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import InvalidPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from rental_property.models import Building, RentalUnit

from utilities_and_rent.forms import SubmitPaymentsForm
from utilities_and_rent.models import RentPayment, UnitRentDetails

User = get_user_model()

@login_required
@user_passes_test(lambda user: user.is_tenant==True, login_url='profile')
def my_rent_details(request, building_slug, unit_slug, username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(slug=unit_slug, building=building)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    
    due_status = request.GET.get('payment_status', '')
    today = datetime.datetime.now()
    today_formatted = today.strftime('%Y-%m-%d')
    
    if due_status == 'due':
        all_rent = UnitRentDetails.objects.filter(tenant=tenant, unit=unit, cleared=False).filter(Q(due_date__lt=today_formatted))
    elif due_status == 'cleared':
        all_rent = UnitRentDetails.objects.filter(tenant=tenant, unit=unit, cleared=True)
    elif due_status == 'upcoming':
        all_rent = UnitRentDetails.objects.filter(tenant=tenant, unit=unit, cleared=False, amount_paid__lte=0).filter(Q(due_date__gte=today_formatted))
    elif due_status == 'un_cleared':
        all_rent = UnitRentDetails.objects.filter(tenant=tenant, unit=unit, cleared=False, amount_paid__gt=0)
    else:
        all_rent = UnitRentDetails.objects.filter(tenant=tenant, unit=unit)
              
    context = {'building':building, 'unit':unit, 'tenant':tenant,'all_rent':all_rent,'due_status':due_status}
    return render(request, 'utilities_and_rent/my-rent-details.html', context)

@login_required
@user_passes_test(lambda user: user.is_tenant==True, login_url='profile')
def submit_payment_record(request, building_slug, unit_slug, rent_code, username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building, slug=unit_slug)
    manager = Managers.objects.get(building_manager__pk=building.id)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    rent = UnitRentDetails.objects.get(code=rent_code, tenant=tenant)
    
    if request.method == 'POST':
        pay_info_form = SubmitPaymentsForm(request.POST)
        if pay_info_form.is_valid():
            pay_info_form.instance.rent_details = rent
            pay_info_form.instance.tenant = tenant
            pay_info_form.instance.manager = manager
            pay_info_form.instance.paid_for_month = rent.pay_for_month
            pay_info_form.save()
            messages.success(request, 'Payment info submitted, update will be done once approved')
            return redirect('my-rent', building_slug=building.slug, unit_slug=unit.slug, username=tenant.associated_account.username)
    else:
        pay_info_form = SubmitPaymentsForm()
        
    context = {'pay_info_form':pay_info_form,'building':building,'rent':rent, 'unit':unit}
    return render(request, 'utilities_and_rent/submit-payments.html', context)

#TODO: update renddetails in update function
#TODO: view payments made
#TODO: manager in admin functions
#TODO: water & electricity tracking
#TODO: graph usage