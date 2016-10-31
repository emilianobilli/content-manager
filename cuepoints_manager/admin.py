from django.contrib import admin

import models

# Register your models here.

@admin.register(models.Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(models.Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'house_id']


@admin.register(models.CuePoint)
class CuePointAdmin(admin.ModelAdmin):
    list_display = ['id', 'video', 'timecode', 'name', 'language']
    search_fields = ['video__house_id']