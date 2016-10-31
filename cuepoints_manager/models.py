from __future__ import unicode_literals

from django.db import models

from django.core.exceptions import ValidationError
import re

# Create your models here.

def validate_timecode(tc):
    valid = re.match("([0-9][0-9]):([0-5][0-9]):([0-5][0-9])(;|:)([0-2][0-9])", tc)
    if not valid:
        raise ValidationError("Timecode incorrecto. Formato: 00:00:00;00")


class Video(models.Model):
    house_id = models.CharField(max_length=10, help_text='Video House ID')

    def __unicode__(self):
        return self.house_id


class Language(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=2)

    def __unicode__(self):
        return self.name


class CuePoint(models.Model):
    video    = models.ForeignKey('Video')
    timecode = models.CharField(max_length=11, validators=[validate_timecode], help_text='Formato: 00:00:00;00')
    name     = models.CharField(max_length=50, help_text='Cuepoint description')
    language = models.ForeignKey('Language')

    def __unicode__(self):
        return ('%s:%s:%s' % (self.video.house_id, self.timecode, self.language.code))
