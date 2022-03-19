import datetime

from utilities_and_rent.models import UnitRentDetails
from django.core.mail import EmailMessage
from config.settings import DEFAULT_FROM_EMAIL
from apscheduler.schedulers.background import BackgroundScheduler
from django.template.loader import render_to_string
import pytz

utc = pytz.UTC

def notify_tenant_rent_nearing_due():
    get_today = datetime.datetime.now().replace(tzinfo=utc)
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

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(notify_tenant_rent_nearing_due, 'interval', minutes=11520) # every 8|11520 days, TODO: reset to 2880 | 48 hour schedule
    scheduler.start()