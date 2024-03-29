from django.contrib import admin

from . import models


class BrandAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


class ModelAdmin(admin.ModelAdmin):
    list_display = ("code", "brand", "name", "fix_price")


class PolicyAdmin(admin.ModelAdmin):
    list_display = ("model", "imei", "phone_number", "status")
    list_filter = ("model", "status", "expiration")


admin.site.register(models.Brand, BrandAdmin)
admin.site.register(models.Model, ModelAdmin)
admin.site.register(models.Policy, PolicyAdmin)
