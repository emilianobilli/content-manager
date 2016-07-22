from django.contrib import admin
import models
# Register your models here.

@admin.register(models.Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'cdnurl' ]

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'api_key', 'access_type' ]

@admin.register(models.Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['house_id']

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'video', 'filename']

