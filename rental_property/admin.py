from django.contrib import admin
from rental_property.models import (Building, Counties, Estate, RentalUnit,
                                    UnitAlbum, UnitType, MaintananceNotice)


class UnitAlbumAdmin(admin.StackedInline):
    model = UnitAlbum

@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'registered_owner', 'registered_country', 'added', 'updated']

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'estate', 'address_line', 'country', 'added', 'updated']


@admin.register(RentalUnit)
class RentalUnitAdmin(admin.ModelAdmin):
    inlines = [UnitAlbumAdmin]
    list_display = ['unit_number', 'building', 'unit_type', 'bathrooms', 'bedrooms', 'status']
    list_filter = ['building',]

@admin.register(UnitType)
class HouseTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'added_by', 'added_by', 'added', 'updated']

@admin.register(Counties)
class CountiesAdmmin(admin.ModelAdmin):
    list_display = ['name','slug','created','updated']
    search_fields = ['name',]
    prepopulated_fields = {'slug': ('name',)}
    
@admin.register(MaintananceNotice)
class MaintananceNoticeAdmin(admin.ModelAdmin):
    list_display = ['notice_by','ref_number','title','from_date','to_date','created']
    list_filter = ['from_date','to_date','created']
    search_fields = ['ref_number','title',]