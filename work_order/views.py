from accounts.models import Managers
from config.settings import DEFAULT_FROM_EMAIL
from core.utils import render_to_pdf
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMessage
from django.shortcuts import (HttpResponse, HttpResponseRedirect, redirect,
                              render)
from django.template.loader import get_template, render_to_string
from rental_property.models import Building

from work_order.filters import HiredPersonnelFilter, WorkOrderFilter
from work_order.forms import (NewHiredPersonnelForm, NewWorkOrderForm,
                              PaymentUpdateForm, PersonnelContactForm,
                              UpdatePersonnelForm, WorkOrderPaymentsForm,
                              WorkOrderUpdateForm)
from work_order.models import (HiredPersonnel, PersonnelContact, WorkOrder,
                               WorkOrderPayments)


@login_required
def hired_personnel(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    user = request.user
    if user.is_manager:
        manager = Managers.objects.get(associated_account=user)
    else:
        return redirect('profile')
    
    personnels = HiredPersonnel.objects.filter(building=building).order_by('-created')
    personnels_filter = HiredPersonnelFilter(request.GET, queryset=personnels)
    
    if request.method == 'POST':
        add_form = NewHiredPersonnelForm(request.POST)
        if add_form.is_valid():
            add_form.instance.building = building
            add_form.instance.personnel_manager = manager
            add_form.save()
            messages.success(request, 'New Personnel added')
            return HttpResponseRedirect("")
    else:
        add_form = NewHiredPersonnelForm()
    
    context = {'building':building,'personnels':personnels_filter,'add_form':add_form}
    return render(request, 'work_order/hired_personnel.html', context)

def hired_personnel_details(request, building_slug, p_code):
    building = Building.objects.get(slug=building_slug)
    personnel = HiredPersonnel.objects.get(building=building, personnel_code=p_code)
    
    if request.method == 'POST':
        p_contact = PersonnelContactForm(request.POST)
        if p_contact.is_valid():
            p_contact.instance.personnel = personnel
            p_contact.save()
            contact = p_contact.instance
            subject = contact.subject
            template = 'work_order/email/contact_email.html'
            html_message = render_to_string(template,
                                            {'contact':contact,})
            from_email = DEFAULT_FROM_EMAIL
            to_email = contact.personnel.personnel_email
            message = EmailMessage(subject, html_message, from_email, [to_email])
            message.content_subtype = 'html'
            message.send()
            messages.success(request, 'Email sent successfully')
            return HttpResponseRedirect("")
    else:
        p_contact = PersonnelContactForm()
        
    context = {'building':building,'personnel':personnel,'p_contact':p_contact}
    return render(request, 'work_order/hired_personel_details.html', context)

def update_hired_personnel(request, building_slug, p_code):
    building = Building.objects.get(slug=building_slug)
    personnel = HiredPersonnel.objects.get(building=building, personnel_code=p_code)
    
    if request.method == 'POST':
        update_form = UpdatePersonnelForm(request.POST, instance=personnel)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, 'Personnel updated successfully')
            return redirect('hired_personnel_details', building_slug=building.slug,
                            p_code=personnel.personnel_code)
    else:
        update_form = UpdatePersonnelForm(instance=personnel)
        
    context = {'building':building,'personnel':personnel,'update_form': update_form,}
    return render(request, 'work_order/update_hired_personel.html', context)

@login_required
def work_orders(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    work_orders = WorkOrder.objects.filter(building=building).order_by('-created')
    
    work_orders_filter = WorkOrderFilter(request.GET, queryset=work_orders)
    
    if request.method == 'POST':
        add_order_form = NewWorkOrderForm(building,request.POST)
        if add_order_form.is_valid():
            add_order_form.instance.building = building    
            add_order_form.save()
            new_order = add_order_form.instance
            if new_order.email_personnel:
                subject = new_order.title
                template = 'work_order/email/new_work_order.html'
                html_message = render_to_string(template,
                                            {'new_order':new_order,})
                from_email = DEFAULT_FROM_EMAIL
                to_email = new_order.assigned_to.personnel_email
                message = EmailMessage(subject, html_message, from_email, [to_email])
                message.content_subtype = 'html'
                message.send()
                messages.success(request, 'Email sent')
                return HttpResponseRedirect("")
    else:
        add_order_form = NewWorkOrderForm(building)
    context = {'building':building,'work_orders':work_orders_filter,'add_order_form':add_order_form}
    return render(request, 'work_order/work_orders.html', context)

@login_required
def work_order_details(request, building_slug, order_code):
    building = Building.objects.get(slug=building_slug)
    order = WorkOrder.objects.get(work_order_code=order_code)
    associated_payments = WorkOrderPayments.objects.filter(parent_order=order)
    
    if request.method == 'POST':
        update_form = WorkOrderUpdateForm(request.POST, instance=order)
        add_payment_form = WorkOrderPaymentsForm(request.POST)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, 'WorkOrder Updated Successfully')
            return HttpResponseRedirect("")
        if add_payment_form.is_valid():
            add_payment_form.instance.parent_order = order
            add_payment_form.save()
            messages.success(request, 'Payment Added')
            return HttpResponseRedirect("")
    else:
        update_form = WorkOrderUpdateForm(instance=order)
        add_payment_form = WorkOrderPaymentsForm()
    
    context = {'building':building,'order':order,'update_form':update_form,
               'add_payment_form':add_payment_form,'associated_payments':associated_payments}
    return render(request, 'work_order/work_order_details.html', context)

@login_required
def update_work_order_payment(request,building_slug, order_code, t_code):
    building = Building.objects.get(slug=building_slug)
    order = WorkOrder.objects.get(work_order_code=order_code)
    payment = WorkOrderPayments.objects.get(parent_order=order,tracking_code=t_code)
    
    if request.method == 'POST':
        update_form = PaymentUpdateForm(request.POST, instance=payment)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, 'payment updated successfully')
            return redirect('work_order_details', building_slug=building.slug,
                            order_code=order.work_order_code)
    else:
        update_form = PaymentUpdateForm(instance=payment)
            
    context = {'building': building,'order': order, 'update_form': update_form,}
    return render(request, 'work_order/update_work_order_payment.html', context)


@login_required
def work_order_pdf(request, building_slug, order_code):
    building = Building.objects.get(slug=building_slug)
    order = WorkOrder.objects.get(work_order_code=order_code)
    
    context = {'order': order, 'building': building}
    
    template = get_template('work_order/pdf/work_order_pdf.html')
    html = template.render(context)
    pdf = render_to_pdf('work_order/pdf/work_order_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf,content_type='application/pdf')
        filename = "work_order_%s" %(order.work_order_code)
        content = "inline; filename='%s'" %(filename)
        download = request.GET.get('download')
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not Found")
