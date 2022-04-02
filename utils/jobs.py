import datetime

from io import BytesIO
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from accounts.models import UserNotifications
from config.settings import DEFAULT_FROM_EMAIL
from core.utils import render_to_pdf
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.template.loader import get_template, render_to_string

from utils.models import MpesaOnline, RentDefaulters, UnitRentDetails
from django.shortcuts import HttpResponse
from xhtml2pdf import pisa

utc = pytz.UTC
get_today = datetime.datetime.now().replace(tzinfo=utc)

def notify_tenant_rent_nearing_due():
    get_in_two_days = get_today + datetime.timedelta(days=2)
    rent_instances = UnitRentDetails.objects.filter(
        status='open', due_date__lte=get_in_two_days,
    )
    recievers = []
    
    for inst in rent_instances:
        recievers.append(inst.tenant.associated_account.email)
        
        subject = "AUTOMATIC RENT PAYMENT NOTIFICATION FOR {0} RENTAL UNIT {1}".format(
            inst.tenant.full_name, inst.unit.unit_number
            )
        html_content = 'utilities_and_rent/mails/send_nearing_due_notification.html'
        html_message = render_to_string(html_content, {'data':inst,})
        from_email = DEFAULT_FROM_EMAIL
        to_email = recievers
        message = EmailMessage(subject, html_message, from_email, to_email)
        message.content_subtype = 'html'
        message.send()
        
def sync_mpesa_payments():
    get_new_mpesa_payments = MpesaOnline.objects.filter(
        ResultCode='0',update_status='recieved',
    )
    for payment in get_new_mpesa_payments:
        if payment.Amount:
            parent = UnitRentDetails.objects.get(id=payment.parent.pk)
            parent.amount_paid += payment.Amount
            parent.save()
            #update the payment
            payment.update_status = 'updated'
            payment.save(update_fields=['update_status',])
            
            message = UserNotifications(
                user_id = payment.tenant.associated_account,
                message = 'Mpesa payment updated',
            )
            message.save()
            
        
def check_and_create_defaulters():
    in_last_60_days = get_today - datetime.timedelta(days=60)
    objs = UnitRentDetails.objects.filter(cleared=False)
    
    for obj in objs:
        if obj.due_date < in_last_60_days:
            try:
                if_exists = RentDefaulters.objects.get(site_account=obj.tenant.associated_account)
                obj.status = 'defaulted'
                obj.save(update_fields=['status',])
            except ObjectDoesNotExist:
                instance = RentDefaulters.objects.create(
                    site_account=obj.tenant.associated_account,
                    tenancy_account = obj.tenant,
                    building = obj.unit.building,
                    )
                instance.save() # create if it dont exist
                obj.status = 'defaulted'
                obj.save(update_fields=['status',])
                
                # notify defaulter
                template = get_template('utilities_and_rent/jobs/notify_defaulter.html')
                context = {'defaulter':instance,'data':obj,}
                html = template.render(context)
                response = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), response)
                pdf = response.getvalue()
                filename = 'defaulted_rent_{0}'.format(instance.tenancy_account.full_name) + '.pdf'
                to_email = instance.site_account.email
                from_email = DEFAULT_FROM_EMAIL
                text = 'Hello, {0}. Please check the attached pdf for your defaulted rent details.'.format(instance.tenancy_account.full_name)
                subject = 'DEFAULTED PAYMENT BUILDING: [{0}]'.format(instance.tenancy_account.rented_unit.building.name)
                message = EmailMessage(subject, text, from_email, [to_email])
                message.attach(filename, pdf, "application/pdf")
                message.send(fail_silently=False)
                
                #create a message
                UserNotifications.objects.create(
                    user_id=obj.tenant.associated_account,
                    message='Added to defaulters'
                )
                    
    
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(notify_tenant_rent_nearing_due, 'interval', minutes=11520) # every 8 days,
    scheduler.add_job(sync_mpesa_payments, 'interval', minutes=2)
    scheduler.add_job(check_and_create_defaulters, 'interval', minutes=1440) # daily check
    scheduler.start()
