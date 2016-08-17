from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Language(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=2)

    def __unicode__(self):
	return self.name


class Subtitle(models.Model):
    enabled	 = models.BooleanField(default=True)
    house_id     = models.CharField(max_length=10)
    language     = models.ForeignKey(Language)
    filename     = models.CharField(max_length=255)
    som		 = models.CharField(max_length=11, default='00:00:00;00')
    timecode_in  = models.CharField(max_length=11, default='', blank=True)	# 00:00:00:00
    timecode_out = models.CharField(max_length=11, default='', blank=True)	
    adjustment   = models.CharField(max_length=12, default='', blank=True)	# [+|-]00:00:00:00 

    def __unicode__(self):
	return ('%s:%s' % (self.house_id,self.language.code))


class Config(models.Model):
    enabled	  = models.BooleanField()
    subtitle_path = models.CharField(max_length=255)

    def __unicode__(self):
	return self.subtitle_path
