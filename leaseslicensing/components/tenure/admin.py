from django.contrib import admin

from leaseslicensing.components.tenure.models import (
    LGA,
    Act,
    Category,
    District,
    Group,
    Name,
    Region,
    SiteName,
    Tenure,
    Vesting,
)


@admin.register(Act)
class ActAdmin(admin.ModelAdmin):
    pass


@admin.register(Tenure)
class TenureAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
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


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(SiteName)
class SiteNameAdmin(admin.ModelAdmin):
    pass


@admin.register(Vesting)
class VestingAdmin(admin.ModelAdmin):
    pass


@admin.register(Name)
class NameAdmin(admin.ModelAdmin):
    pass
