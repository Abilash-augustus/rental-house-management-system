from complaints.models import HelpContacts
from accounts.models import Tenants,Managers
from rental_property.models import Building

def get_contacts(request):
    user = request.user
    
    if user.is_authenticated:
        if user.is_tenant:
            tenant = Tenants.objects.get(associated_account=user)
            building = Building.objects.get(id=tenant.rented_unit.building_id)
            contacts = HelpContacts.objects.filter(associated_building=building)
            return dict(contacts=contacts)
        elif user.is_manager:
            contacts = HelpContacts.objects.all()
            return dict(contacts=contacts)
        else:
            contacts = HelpContacts.objects.filter(make_publicly_available=True)
            return dict(contacts=contacts)
    else:
        contacts = HelpContacts.objects.filter(make_publicly_available=True)
        return dict(contacts=contacts)