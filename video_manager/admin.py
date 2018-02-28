from django.contrib import admin
import models
# Register your models here.

@admin.register(models.Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'cdnurl' ]

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'api_key', 'access_type', 'auth_method', 'gatra_post' ]

@admin.register(models.Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['house_id']
    search_fields = ['house_id']

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'video', 'filename']

@admin.register(models.Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'idp_code','token', 'video', 'expiration']

@admin.register(models.CdnSecret)
class CdnSecretAdmin(admin.ModelAdmin):
    list_display = ['enabled', 'gen', 'key']

@admin.register(models.ProfileFile)
class ProfileFileAdmin(admin.ModelAdmin):
    list_display = ['profile', 'filename']

@admin.register(models.AuthMethod)
class AuthMethodAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(models.Cdn)
class CdnAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(models.ToolboxCache)
class ToolboxCacheAdmin(admin.ModelAdmin):
    list_display = ['user_token','urn']

