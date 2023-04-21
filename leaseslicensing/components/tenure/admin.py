from django.contrib import admin

from leaseslicensing.components.tenure.models import LGA, District, Group, Region


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    pass


@admin.register(LGA)
class LGAAdmin(admin.ModelAdmin):
    pass
