from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from rental_property.models import Building, RentalUnit

from accounts.forms import (AddManagerForm, ProfileUpdateForm, TenantsForm,
                            UserUpdateForm)
from accounts.models import Managers, Profile, Tenants

User = get_user_model()

@login_required
def my_profile(request):
    user = request.user
    if user.is_tenant:
        tenant_instance = Tenants.objects.get(user=user)
    else:
        tenant_instance = False
        
    context = {'user': user, 'tenant_instance':tenant_instance}
    return render(request, 'accounts/profile.html', context)

# individual profile & user update
@ login_required
def profile_info_update(request):
    if request.method == 'POST':
        user_update_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_update_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_update_form.is_valid() and profile_update_form.is_valid():
            user_update_form.save()
            profile_update_form.save()
            messages.success(request, 'Profile was updated successfully!')
            return redirect('profile')
    else:
        user_update_form = UserUpdateForm(instance=request.user)
        profile_update_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'user_form': user_update_form, 'profile_form': profile_update_form,}
    return render(request, 'accounts/profile-settings.html', context)

# add a manager.
@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='available-units')
def add_new_manager(request):
    if request.method == 'POST':
        managerform = AddManagerForm(request.POST, request.FILES)
        if managerform.is_valid():
            managerform.instance.added_by = request.user
            managerform.save()
            return redirect('/')
    else:
        managerform = AddManagerForm()
    context = {'managerform': managerform,}
    return render(request, 'accounts/add-manager.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='available-units')
def view_tenant_profile(request, building_slug, username):
    building = Building.objects.get(slug=building_slug)
    user_instance = User.objects.get(username=username)
    tenant_instance = Tenants.objects.get(user_id=user_instance, rented_unit__building=building)
    context = {'tenant_instance': tenant_instance, 'user_instance':user_instance}
    return render(request, 'accounts/view-tenant.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='available-units')
def add_tenant(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    if request.method == 'POST':
        new_tenant_form = TenantsForm(building, request.POST)
        if new_tenant_form.is_valid():
            new_tenant_form.save()
            messages.success(request, 'Tenant was created successfully!')
            return redirect('operational-buildings')
    else:
        new_tenant_form = TenantsForm(building)
    context = {'new_tenant_form': new_tenant_form}
    return render(request, 'accounts/new-tenant.html', context)


@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='available-units')
def update_tenant(request, building_slug, username):
    building = Building.objects.get(slug=building_slug)
    tenant_user = User.objects.get(username=username)
    tenant = Tenants.objects.get(user_id=tenant_user, rented_unit__building=building)

    if request.method == 'POST':
        tenant_form = TenantsForm(building, request.POST, instance=tenant)
        if tenant_form.is_valid():
            tenant_form.instance.user = tenant_user
            tenant_form.save()
            messages.success(request, 'Tenant was updated successfully!')
            return redirect('operational-buildings')
    else:
        tenant_form = TenantsForm(building, instance=tenant)
    context = {'tenant_user':tenant_user,'tenant_form': tenant_form}
    return render(request, 'accounts/update-tenant.html', context)
