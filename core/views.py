import datetime

from accounts.models import Managers, Tenants
from complaints.models import Complaints, UnitReport
from config.settings import DEFAULT_FROM_EMAIL
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.db.models import Count, Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import HttpResponse, redirect, render
from django.template.loader import get_template, render_to_string
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from django.views.generic import CreateView
from rental_property.models import Building, MaintananceNotice, RentalUnit
from utils.models import ElectricityBilling, WaterBilling

from core.filters import (CommsFilter, ContactFilter, EvictionNoticeFilter,
                          MoveOutNoticeFilter, MyNoticeFilter,
                          VisitFilter)
from core.forms import (CancelMoveOutForm, ContactForm, ContactReplyForm,
                        EvictionNoticeForm, FromTenantForm,
                        NewMoveOutNoticeForm, NewTenantEmailForm, UnitTourForm,
                        UpdateEvictionNotice, UpdateMoveOutNotice,
                        VisitUpdateForm)
from core.models import (Contact, ContactReply, EvictionNotice,
                         ManagerTenantCommunication, MoveOutNotice,
                         TenantEmails, UnitTour)
from core.utils import render_to_pdf

User = get_user_model()

#visitor contact
class CreateContact(SuccessMessageMixin, CreateView):
    model = Contact
    form_class = ContactForm
    success_message = "Your contact has been submitted."
    success_url = reverse_lazy('operational-buildings')
    
@login_required
def view_contacts(request):
    contacts = Contact.objects.all().order_by('-created')
    contacts_filter = ContactFilter(request.GET,queryset=contacts)
    context = {'recieved_contacts': contacts_filter}
    return render(request, 'core/contacts_view.html',context)

@login_required
def contact_reply(request,ref_code):
    contact = Contact.objects.get(ref_code=ref_code)
    replies = ContactReply.objects.filter(parent=contact)
    
    if request.method == 'POST':
        reply_form = ContactReplyForm(request.POST)
        if reply_form.is_valid():
            reply_form.instance.parent = contact
            reply_form.save()
            contact.status = 'closed'
            contact.save(update_fields=['status',])
            messages.success(request,'reply sent')
            get_message = reply_form.instance
            replied_by = request.user
            manager = Managers.objects.get(associated_account=replied_by)
            subject = 'RESPONSE TO YOUR CONTACT ON: {0}'.format(SimpleLazyObject(lambda: get_current_site(request)))
            html_content = 'core/mail/contact_reply.html'
            html_message = render_to_string(html_content, {'my_contact':get_message,'manager':manager})
            from_email = DEFAULT_FROM_EMAIL
            to_email = contact.email
            message = EmailMessage(subject, html_message, from_email, [to_email])
            message.content_subtype = 'html'
            message.send()
            messages.info(request, 'Locking contact')
            return redirect('core:contact_reply',ref_code=contact.ref_code)
    else:
        reply_form = ContactReplyForm(request.POST)
    
    context = {'r_contact':contact,'reply_form':reply_form,'replies':replies}
    return render(request, 'core/contact_reply.html', context)
    

#visits
def schedule_unit_tour(request, unit_slug):
    unit = RentalUnit.objects.get(slug=unit_slug)

    if request.method == 'POST':
        tour_form = UnitTourForm(request.POST)
        if tour_form.is_valid():
            tour_form.instance.unit = unit
            tour_form.save()
            messages.success(request, 'Visit has been added, you will receive an email concerning any action.')
            return redirect('unit-details', building_slug=unit.building.slug, unit_slug=unit.slug)
    else:
        tour_form = UnitTourForm()
    context = {'unit': unit, 'tour_form': tour_form}
    return render(request, 'core/visit_unit.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def scheduled_visits(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    
    visits = UnitTour.objects.filter(unit__building=building).order_by('-created')
    visits_filter = VisitFilter(request.GET, queryset=visits)
    
    visited = UnitTour.objects.filter(unit__building=building,visit_status='visited').count()
    waiting = UnitTour.objects.filter(unit__building=building,visit_status='waiting').count()
    cancelled = UnitTour.objects.filter(unit__building=building,visit_status='visited').count()

    context = {'building':building, 'visits':visits_filter,
               'visited':visited,'waiting':waiting,'cancelled':cancelled}
    return render(request, 'core/vists_manager.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_view_visits(request, building_slug, visit_code):
    building = Building.objects.get(slug=building_slug)
    visit = UnitTour.objects.get(visit_code=visit_code, unit__building=building)

    last_updated_by = Managers.objects.get(associated_account=request.user)

    if request.method == 'POST':
        update_visit_form = VisitUpdateForm(request.POST, instance=visit)
        if update_visit_form.is_valid():
            update_visit_form.instance.last_updated_by = last_updated_by
            update_visit_form.save()
            check_status = update_visit_form.instance.visit_status
            
            if check_status == 'cancelled' or check_status == 'approved':
                subject = 'ACTION ON OUR VISIT REF: {0}'.format(visit.visit_code)
                html_content = 'core/mail/confirm-visit.html'
                html_message = render_to_string(html_content, {'building':building,'visit':visit})
                from_email = DEFAULT_FROM_EMAIL
                to_email = visit.visitor_email
                message = EmailMessage(subject, html_message, from_email, [to_email])
                message.content_subtype = 'html'
                message.send()
            messages.success(request, 'Visit was updated successfully')
            return redirect('core:visits', building_slug=building.slug)
    else:
        update_visit_form = VisitUpdateForm(instance=visit)
    context = {'visit':visit, 'update_visit_form': update_visit_form, 'building':building}
    return render(request, 'core/visits-update.html', context)

#move out notice
@login_required
@user_passes_test(lambda user: user.is_tenant==True, login_url='profile')
def my_move_out_notice(request, building_slug, username):
    building = Building.objects.get(slug=building_slug)
    user_instance = User.objects.get(username=username)
    tenant = Tenants.objects.get(associated_account=user_instance, rented_unit__building=building)
    
    check_if_notice_exists = MoveOutNotice.objects.filter(tenant=tenant,notice_status='received')
    if check_if_notice_exists:
        messages.success(request, 'You already have an active notice in place')
        messages.info(request, 'Operation not allowed')
        return redirect('profile')
    else:
        if request.method == 'POST':
            vacate_form = NewMoveOutNoticeForm(request.POST)
            if vacate_form.is_valid():
                vacate_form.instance.tenant = tenant
                vacate_form.save()
                get_notice = vacate_form.instance
                subject = 'MOVE OUT NOTICE FOR {0} ON UNIT {1}'.format(get_notice.tenant.full_name,get_notice.tenant.rented_unit.unit_number)
                html_content = 'core/mail/move_out_notice.html'
                html_message = render_to_string(html_content, {'building':building,'data':get_notice})
                from_email = DEFAULT_FROM_EMAIL
                to_email = building.manager.associated_account.email
                message = EmailMessage(subject, html_message, from_email, [to_email])
                message.content_subtype = 'html'
                message.send()
                messages.success(request, 'Your notice has been sent')
                return HttpResponseRedirect('')
        else:
            vacate_form = NewMoveOutNoticeForm()
        
    context = {'vacate_form':vacate_form, 'building':building, 'tenant':tenant,
               'check_if_notice_exists':check_if_notice_exists}
    return render(request, 'core/my_vacate_notice.html', context)

@login_required
def my_notices_(request,building_slug,unit_slug,username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    notices = MoveOutNotice.objects.filter(tenant=tenant)
    maintanance_notices = MaintananceNotice.objects.filter(building=building).order_by('-created')[:12]
    eviction_notices = EvictionNotice.objects.filter(tenant=tenant,unit=unit)
    notices_filter = MyNoticeFilter(request.GET, queryset=notices)
    
    
    context = {'building':building,'notices':notices_filter,'tenant':tenant,
               'eviction_notices':eviction_notices,'maintanance_notices':maintanance_notices}
    return render(request, 'core/my_notices.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def move_out_notice_update(request, building_slug, notice_code):
    building = Building.objects.get(slug=building_slug)
    notice = MoveOutNotice.objects.get(tenant__rented_unit__building=building, code=notice_code)
    
    if request.method == 'POST':
        v_update_form = UpdateMoveOutNotice(request.POST, instance=notice)
        if v_update_form.is_valid():
            v_update_form.save()
            messages.success(request, 'Status changed')
            return redirect('core:move-out-notices', building_slug=building.slug)
    else:
        v_update_form = UpdateMoveOutNotice(instance=notice)
    context = {'v_update_form':v_update_form,'notice':notice,'building':building,}
    return render(request, 'core/move_out_notice_update.html', context)

@login_required
@user_passes_test(lambda user: user.is_tenant==True, login_url='profile')
def cancel_move_out_notice(request, building_slug, notice_code, username):
    building = Building.objects.get(slug=building_slug)
    user_instance = User.objects.get(username=username)
    tenant = Tenants.objects.get(associated_account=user_instance, rented_unit__building=building)
    notice_instance = MoveOutNotice.objects.get(tenant=tenant, code=notice_code)
    
    if request.method == 'POST':
        cancel_form = CancelMoveOutForm(request.POST, instance=notice_instance)
        if cancel_form.is_valid():
            cancel_form.save()
            MoveOutNotice.objects.filter(tenant=tenant).update(notice_status='dropped')
            messages.success(request, 'Your notice has been updated')
            return redirect('core:my_move_out_notices', building_slug=building.slug,
                            unit_slug=tenant.rented_unit.slug, username=tenant.associated_account.username)
    else:
        cancel_form = CancelMoveOutForm(instance=notice_instance)
        
    context = {'cancel_form':cancel_form, 'building':building, 'tenant':tenant,
               'notice_instance':notice_instance}
    return render(request, 'core/cancel-notice.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def move_out_notices(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    move_out_notices = MoveOutNotice.objects.filter(tenant__rented_unit__building=building)
    move_out_notices_filter = MoveOutNoticeFilter(request.GET, queryset=move_out_notices)
    
    context = {'move_out_notices':move_out_notices_filter, 'building':building}
    return render(request, 'core/move-out-notices.html', context)

@login_required
def move_out_pdf(request,building_slug, unit_slug, username, notice_code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    active_user = request.user
    
    if active_user.is_manager or tenant:
        notice = MoveOutNotice.objects.get(tenant=tenant,code=notice_code)
    else:
        return redirect('profile')
    
    context = {'notice':notice,'building':building,'tenant':tenant}
    template = get_template('pdf/move_out_notice.html')
    html = template.render(context)
    pdf = render_to_pdf('pdf/move_out_notice.html', context)
    if pdf:
        response = HttpResponse(pdf,content_type='application/pdf')
        filename = "move_out_notice_%s" %(tenant.full_name)
        content = "inline; filename='%s'" %(filename)
        download = request.GET.get('download')
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not Found")


#eviction notices
@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def create_eviction_notice(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    manager = Managers.objects.get(associated_account__username=request.user.username)

    if request.method == 'POST':
        eviction_form = EvictionNoticeForm(building,request.POST)
        if eviction_form.is_valid():
            eviction_form.instance.sent_by = manager
            get_tenant = eviction_form.instance.tenant
            eviction_form.instance.building = building
            eviction_form.instance.unit = RentalUnit.objects.get(pk=get_tenant.rented_unit.id)         
            eviction_form.save()
            e_data = eviction_form.instance
            if e_data.send_email:
                subject = 'EVICTION NOTICE FOR {0} ON UNIT {1}'.format(e_data.tenant.full_name,e_data.unit.unit_number)
                html_content = 'core/mail/eviction_notice.html'
                html_message = render_to_string(html_content, {'building':building,'data':e_data})
                from_email = DEFAULT_FROM_EMAIL
                to_email = e_data.tenant.associated_account.email
                message = EmailMessage(subject, html_message, from_email, [to_email])
                message.content_subtype = 'html'
                message.send()
            
            messages.success(request, 'Eviction notice has been sent!')
            return redirect('core:evictions', building_slug=building.slug)
    else:
        eviction_form = EvictionNoticeForm(building)
    
    context = {'eviction_form':eviction_form,'building':building}
    return render(request, 'core/create-eviction-notice.html', context)


@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def view_eviction_notices(request,building_slug):
    building = Building.objects.get(slug=building_slug)
    
    notices = EvictionNotice.objects.filter(unit__building=building).order_by('-created')
    notices_filter = EvictionNoticeFilter(request.GET, queryset=notices)
    
    context = {'notices':notices_filter, 'building':building}
    return render(request, 'core/view-eviction-notices.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def eviction_notice_display(request,building_slug, notice_code):
    building = Building.objects.get(slug=building_slug)
    notice = EvictionNotice.objects.get(unit__building=building, notice_code=notice_code)
    if request.method == 'POST':
        update_form = UpdateEvictionNotice(request.POST, instance=notice)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, 'Notice Updated')
            return HttpResponseRedirect("")
    else:
        update_form = UpdateEvictionNotice(instance=notice)
        
    context = {'building':building, 'notice':notice,'update_form':update_form}
    return render(request, 'core/e-notice-display.html', context)

@login_required
def eviction_view_pdf(request,building_slug, unit_slug, username, code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    active_user = request.user
    
    if active_user.is_manager or tenant:
        notice = EvictionNotice.objects.get(tenant=tenant,notice_code=code)
    else:
        return redirect('profile')
    
    context = {'notice':notice,'building':building,'tenant':tenant}
    template = get_template('pdf/eviction_notice.html')
    html = template.render(context)
    pdf = render_to_pdf('pdf/eviction_notice.html', context)
    if pdf:
        response = HttpResponse(pdf,content_type='application/pdf')
        filename = "eviction_notice_%s" %(tenant.full_name)
        content = "inline; filename='%s'" %(filename)
        download = request.GET.get('download')
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not Found")

#general communications | emails archive
@login_required
def general_communications(request,building_slug):
    building = Building.objects.get(slug=building_slug)
    communications = ManagerTenantCommunication.objects.filter(building=building).order_by('-created')
    comm_filter = CommsFilter(request.GET, queryset=communications)
    filter_form = comm_filter.form
    comm_filter = comm_filter.qs
    paginator = Paginator(comm_filter, 5)
    page = request.GET.get('page')
    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)

    context = {
        'comms': response,'building': building,'filter_form':filter_form,
    }
    return render(request, 'core/general_comms.html', context)


@login_required
def new_email(request,building_slug):
    building = Building.objects.get(slug=building_slug)
    manager = Managers.objects.get(associated_account=request.user)
    
    tenants = Tenants.objects.filter(rented_unit__building=building)
    recipients = []
    for tenant in tenants:
        recipients.append(tenant.associated_account.email)
    
    if request.method == 'POST':
        new_email =NewTenantEmailForm(building,request.POST)
        if new_email.is_valid():
            new_email.instance.sent_by = manager
            new_email.instance.building = building
            new_email.save()
            data = new_email.instance
            
            if data.send_to_all:
                send_to_emails = recipients
            else:
                get_recipients = data.sent_to.all()
                select_recipients = []
                for t in get_recipients:
                    select_recipients.append(t.associated_account.email)
                send_to_emails = select_recipients
            
            subject = data.subject
            template = 'core/mail/tenant_email.html'
            html_message = render_to_string(template,{'data':data,'manager':manager})
            from_email = DEFAULT_FROM_EMAIL
            to_email = send_to_emails
            message = EmailMessage(subject, html_message, from_email, to_email)
            message.content_subtype = 'html'
            message.send()
            messages.success(request, 'Email sent successfully')
            return redirect('core:general_communications', building_slug=building.slug)
    else:
        new_email = NewTenantEmailForm(building)
    context = {
        'building':building,'new_email':new_email,
    }
    return render(request, 'core/new_email.html', context)

@login_required
def email_archive_view(request,building_slug,ref_number):
    building = Building.objects.get(slug=building_slug)
    archive = ManagerTenantCommunication.objects.get(building=building,ref_number=ref_number)
    
    context = {
        'building': building,'archive':archive,
    }
    return render(request, 'core/email_archive.html', context)


@login_required
def my_mails(request,building_slug,username):
    building = Building.objects.get(slug=building_slug)
    user = request.user
    if not user.is_tenant:
        return redirect('profile')
    else:
        tenant = Tenants.objects.get(associated_account__username=username)
        
        type_click = request.GET.get('type', 'inbox')
        if 'sent' in type_click:
            mails = TenantEmails.objects.filter(sent_by=tenant,building=building).order_by('-created')[:14]
        elif 'inbox' in type_click:
            general_mails = ManagerTenantCommunication.objects.filter(building=building,send_to_all=True,retract=False
                                                                      ).order_by('-created')[:7]
            my_mails = ManagerTenantCommunication.objects.filter(sent_to=tenant,retract=False
                                                                 ).order_by('-created')[:7]
            mails = general_mails|my_mails
        else:
            messages.info(request, 'Action forbidden!!! Redirected to inbox.')  
            return redirect('core:my_mails', building_slug=building.slug, username=tenant.associated_account.username)
      
    context = {
        'mails': mails,'building':building,'tenant':tenant,
        }
    return render(request, 'core/my_email_archive_list.html', context)

@login_required
def my_archive_details(request,building_slug,username,ref_number):
    building = Building.objects.get(slug=building_slug)
    tenant = Tenants.objects.get(associated_account__username=username)
    archive = ManagerTenantCommunication.objects.get(building=building,ref_number=ref_number)
    
    context = {
        'building': building,'tenant':tenant,'archive':archive,
    }
    return render(request, 'core/my_archive_details.html', context)

@login_required
def view_tenant_archive(request,building_slug,username,ref_number):
    building = Building.objects.get(slug=building_slug)
    tenant = Tenants.objects.get(rented_unit__building=building,associated_account__username=username)
    archive = TenantEmails.objects.get(sent_by=tenant,ref_number=ref_number)
    
    context = {'building': building,'archive':archive,'tenant':tenant}
    return render(request, 'core/view_tenant_archive.html', context)

@login_required
def send_email_to_manager(request,building_slug,username):
    building = Building.objects.get(slug=building_slug)
    user = request.user
    if not user.is_tenant:
        return redirect('profile')
    else:
        tenant = Tenants.objects.get(associated_account__username=username)
        manager = Managers.objects.get(pk=building.manager.id)
        
        if request.method == 'POST':
            new_mail = FromTenantForm(request.POST)
            if new_mail.is_valid():
                new_mail.instance.sent_by = tenant
                new_mail.instance.sent_to = manager
                new_mail.instance.building = building    
                new_mail.save()
                get_data = new_mail.instance
                subject = get_data.subject
                template = 'core/mail/to_manager_email.html'
                html_message = render_to_string(template,{'data':get_data,'manager':manager})
                from_email = DEFAULT_FROM_EMAIL
                to_email = get_data.building.manager.associated_account.email
                message = EmailMessage(subject, html_message, from_email, [to_email])
                message.content_subtype = 'html'
                message.send()
                messages.success(request, 'Mail sent successfully')
                return redirect('core:my_mails', building_slug=building.slug,
                                username=tenant.associated_account.username)
        else:
            new_mail = FromTenantForm()
        context = {
            'building': building,'tenant':tenant,'new_mail':new_mail,
        }
        return render(request, 'core/new_mail_to_manager.html', context)

#charts
@login_required
def visits_overview(request,building_slug):
    building = Building.objects.get(slug=building_slug)
    
    labels = []
    data = []
    
    queryset = UnitTour.objects.filter(unit__building=building).values(
        'visit_status').annotate(count=Count('visit_status'))
    
    for entry in queryset:
        labels.append(entry['visit_status'])
        data.append(entry['count'])
    
    data = {'labels': labels,'data': data}
    return JsonResponse(data)

@login_required
def evictions_overview(request,building_slug):
    building = Building.objects.get(slug=building_slug)
    
    labels = []
    data = []
    
    queryset = EvictionNotice.objects.filter(unit__building=building).values(
        'eviction_status').annotate(count=Count('eviction_status'))
    
    for entry in queryset:
        labels.append(entry['eviction_status'])
        data.append(entry['count'])
    
    data = {'labels': labels,'data': data}
    return JsonResponse(data)

@login_required
def moveouts_overview(request,building_slug):
    building = Building.objects.get(slug=building_slug)
    
    labels = []
    data = []
    
    queryset = MoveOutNotice.objects.filter(tenant__rented_unit__building=building).values(
        'notice_status').annotate(count=Count('notice_status'))
    
    for entry in queryset:
        labels.append(entry['notice_status'])
        data.append(entry['count'])
    
    data = {'labels': labels,'data': data}
    return JsonResponse(data)

#Errors
def custom_system_error_view(request, exception=None):
    return render(request, "500.html", {})