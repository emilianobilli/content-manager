from django.contrib import admin

import models

# Register your models here.

@admin.register(models.Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(models.Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'enabled']

@admin.register(models.SubtitleFile)
class SubtitleFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(models.Subtitle)
class SubtitleAdmin(admin.ModelAdmin):
    list_display = ['id', 'house_id', 'file']

