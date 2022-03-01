import datetime

from accounts.models import Managers, Tenants
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import InvalidPage, PageNotAnInteger, Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from rental_property.models import Building, RentalUnit

from utilities_and_rent.filters import (PaymentsFilter, RentDetailsFilter,
                                        UnitTypeFilter)
from utilities_and_rent.forms import (AddRentDetailsForm, PaymentUpdateForm,
                                      SubmitPaymentsForm, UpdateRentDetails)
from utilities_and_rent.models import (PaymentMethods, RentPayment,
                                       UnitRentDetails, WaterBilling,
                                       WaterConsumption)

User = get_user_model()

@login_required
@user_passes_test(lambda user: user.is_tenant==True, login_url='profile')
def my_rent_details(request, building_slug, unit_slug, username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(slug=unit_slug, building=building)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    payment_options = PaymentMethods.objects.all()
    
    due_status = request.GET.get('payment_status', '')
    today = datetime.datetime.now()
    today_formatted = today.strftime('%Y-%m-%d')
    
    if due_status == 'due':
        all_rent = UnitRentDetails.objects.filter(tenant=tenant, unit=unit, cleared=False).filter(Q(due_date__lt=today_formatted)).order_by('due_date')
    elif due_status == 'cleared':
        all_rent = UnitRentDetails.objects.filter(tenant=tenant, unit=unit, cleared=True).order_by('due_date')
    elif due_status == 'upcoming':
        all_rent = UnitRentDetails.objects.filter(tenant=tenant, unit=unit, cleared=False, amount_paid__lte=0).filter(Q(due_date__gte=today_formatted)).order_by('due_date')
    elif due_status == 'un_cleared':
        all_rent = UnitRentDetails.objects.filter(tenant=tenant, unit=unit, cleared=False, amount_paid__gt=0).order_by('due_date')
    else:
        all_rent = UnitRentDetails.objects.filter(tenant=tenant, unit=unit).order_by('due_date')
              
    context = {'building':building, 'unit':unit, 'tenant':tenant,'all_rent':all_rent,'due_status':due_status,'payment_options':payment_options}
    return render(request, 'utilities_and_rent/my-rent-details.html', context)

@login_required
@user_passes_test(lambda user: user.is_tenant==True, login_url='profile')
def submit_payment_record(request, building_slug, unit_slug, rent_code, username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building, slug=unit_slug)
    manager = Managers.objects.get(building_manager__pk=building.id)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    rent = UnitRentDetails.objects.get(code=rent_code, tenant=tenant)
    previous_payments = RentPayment.objects.filter(tenant=tenant, tenant__rented_unit=unit, rent_details=rent)
    
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
        
    context = {'pay_info_form':pay_info_form,'building':building,'rent':rent,
               'tenant':tenant,'unit':unit,'previous_payments':previous_payments}
    return render(request, 'utilities_and_rent/submit-payments.html', context)


@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def rent_and_utilities(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    tenants = Tenants.objects.filter(rented_unit__building=building)
    tenants_filter = UnitTypeFilter(request.GET, queryset=tenants)
    
    context = {'building':building, 'tenants_filter':tenants_filter}
    return render(request, 'utilities_and_rent/building_utility_and_rent.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def add_rent(request, building_slug, unit_slug):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building, slug=unit_slug)
    if unit.status == 'occupied':
        tenant = Tenants.objects.get(rented_unit=unit)
        if request.method == 'POST':
            rent_form = AddRentDetailsForm(request.POST)
            if rent_form.is_valid():
                rent_form.instance.tenant = tenant
                rent_form.instance.unit = unit
                rent_form.save()
                # add email notification
                messages.success(request, 'Rent added successfully')
                return redirect('rent-and-utilities', building_slug=building.slug)
        else:
            rent_form = AddRentDetailsForm()
    else:
        messages.success(request, 'The rental unit is empty')
        return redirect('rent-and-utilities', building_slug=building.slug)
    context = {'rent_form':rent_form, 'building':building, 'unit':unit, 'tenant':tenant}
    return render(request, 'utilities_and_rent/add-rent.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def unit_rent_history(request, building_slug, unit_slug, username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(slug=unit_slug, building=building)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    rent_details = UnitRentDetails.objects.filter(tenant=tenant, unit=unit)
    rental_details_filter = RentDetailsFilter(request.GET, queryset=rent_details)
    
    context = {'building': building,'unit':unit,
               'tenant':tenant,'rent_details':rental_details_filter}
    return render(request, 'utilities_and_rent/rent-history.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def managers_update_tenant_rent(request, building_slug, unit_slug, username, rent_code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    rent_details = UnitRentDetails.objects.get(tenant=tenant, code=rent_code)
    
    if request.method == 'POST':
        update_form = UpdateRentDetails(request.POST, instance=rent_details)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, 'Rent updated successfully')
            #TODO: email when notify user = True
            return HttpResponseRedirect("")
    else:
        update_form = UpdateRentDetails(instance=rent_details)
    
    payments = RentPayment.objects.filter(rent_details=rent_details)
    payment_filter = PaymentsFilter(request.GET, queryset=payments)
    
    context = {'update_form':update_form,'building':building,'unit':unit,'tenant':tenant,'rent_details':rent_details,
               'payments':payment_filter,}
    return render(request, 'utilities_and_rent/manager-update-view-payments.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_rent_payment(request, building_slug, unit_slug, username, rent_code, track_code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    parent_rent =  UnitRentDetails.objects.get(tenant=tenant, code=rent_code)
    payment = RentPayment.objects.get(rent_details=parent_rent, tracking_code=track_code)
    
    if request.method == 'POST':
        pay_update_form = PaymentUpdateForm(request.POST, instance=payment)
        if pay_update_form.is_valid():
            pay_update_form.save()
            if pay_update_form.instance.status=='approved':
                update_rent = parent_rent
                update_rent.amount_paid += pay_update_form.instance.amount
                update_rent.save()
            messages.success(request, 'Payment updated successfully')
            return HttpResponseRedirect("")
    else:
        pay_update_form = PaymentUpdateForm(instance=payment)
    
    context = {'building': building,'unit':unit,'tenant':tenant,'pay_update_form':pay_update_form,
               'parent_rent':parent_rent,'payment':payment}
    return render(request, 'utilities_and_rent/rent-payment-update.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def manager_water_billing(request, building_slug, unit_slug, username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    water_billing_set = WaterBilling.objects.filter(rental_unit=unit,tenant=tenant)
    
    context = {
        'building':building,'unit':unit,'tenant':tenant,'water_billing_set':water_billing_set,
    }
    return render(request, 'utilities_and_rent/manager-water-billing.html', context)
    
#TODO: update rent details in update function
#TODO: view payments made
#TODO: manager in admin functions
#TODO: water & electricity tracking
#TODO: graph usage

@login_required
def rent_chart(request,building_slug,unit_slug,username):
    labels = []
    data = []
    
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    
    queryset = UnitRentDetails.objects.filter(tenant=tenant,unit=unit).values(
        'pay_for_month').annotate(rent_amount=Sum('rent_amount')).order_by('added')[:6]
    
    for entry in queryset:
        labels.append(entry['pay_for_month'])
        data.append(entry['rent_amount'])
    
    data = {
        'labels': labels,
        'data': data,
    }
    return JsonResponse(data)

@login_required
def tenant_water_usage(request,building_slug,unit_slug,username):
    labels = []
    data = []
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    queryset = WaterConsumption.objects.filter(
        parent__rental_unit=unit,parent__tenant=tenant).values('reading_added').annotate(
            consumption=Sum('consumption')).order_by('reading_added')[:8]
    
    for entry in queryset:
        labels.append(entry['reading_added'])
        data.append(entry['consumption'])
    
    data = {'labels':labels,'data':data}
    return JsonResponse(data)