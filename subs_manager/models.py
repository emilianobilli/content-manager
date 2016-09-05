from __future__ import unicode_literals

from django.db import models

from django.core.exceptions import ValidationError
import re

# Create your models here.

def validate_timecode(tc):
    valid = re.match("([0-9][0-9]):([0-5][0-9]):([0-5][0-9])(;|:)([0-2][0-9])", tc)
    if not valid:
        raise ValidationError("Timecode incorrecto. Formato: 00:00:00;00")

def validate_adj_tc(tc):
    valid = re.match("(\+|-)([0-9][0-9]):([0-5][0-9]):([0-5][0-9])(;|:)([0-2][0-9])", tc)
    if not valid:
        raise ValidationError("Timecode incorrecto. Formato: +00:00:00;00 | -00:00:00;00")


class Language(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=2)

    def __unicode__(self):
	return self.name

class SubtitleFile(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
	return self.name


class Subtitle(models.Model):
    enabled	 = models.BooleanField(default=True)
    house_id     = models.CharField(max_length=10)
    language     = models.ForeignKey(Language)
    file	 = models.ForeignKey(SubtitleFile)
    som		 = models.CharField(max_length=11, default='00:00:00;00', validators=[validate_timecode], help_text='Formato: 00:00:00;00')
    timecode_in  = models.CharField(max_length=11, default='', blank=True, validators=[validate_timecode], help_text='Formato: 00:00:00;00')	# 00:00:00:00
    timecode_out = models.CharField(max_length=11, default='', blank=True, validators=[validate_timecode], help_text='Formato: 00:00:00;00')	
    adjustment   = models.CharField(max_length=12, default='', blank=True, validators=[validate_adj_tc], help_text='Formato: [+|-]00:00:00;00')	# [+|-]00:00:00:00 

    def __unicode__(self):
	return ('%s:%s' % (self.house_id,self.language.code))


class Config(models.Model):
    enabled	  = models.BooleanField()
    subtitle_path = models.CharField(max_length=255)

    def __unicode__(self):
	return self.subtitle_path
