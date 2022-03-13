from accounts.models import Managers

from rental_property.models import Building, Counties


def my_managed_buildings(request):
    user_instance = request.user
    
    if user_instance.is_authenticated:
        manager_instance = Managers.objects.filter(associated_account=user_instance)[:1]
        managed_buildings = Building.objects.filter(manager=manager_instance)
        return dict(managed_buildings=managed_buildings)
    else:
        return {'False': False,}
