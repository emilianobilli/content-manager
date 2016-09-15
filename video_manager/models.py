from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Video(models.Model):
    house_id   = models.CharField(max_length=10)
    format     = models.CharField(max_length=10, default='hls')

    def __unicode__(self):
        return '%s:%s' % (self.format,self.house_id)



class ProfileFile(models.Model):
    profile	    = models.ForeignKey('Profile')
    number	    = models.IntegerField()
    extinf	    = models.CharField(max_length=20)
    filename	    = models.CharField(max_length=255)

    def __unicode__(self):
	return self.filename



class Profile(models.Model):
    video      = models.ForeignKey('Video')
    bandwidth  = models.CharField(max_length=50)
    average    = models.CharField(max_length=50)
    codecs     = models.CharField(max_length=100)
    resolution = models.CharField(max_length=50)
    filename   = models.CharField(max_length=255)
    version         = models.CharField(max_length=1)
    media_seq  	    = models.CharField(max_length=5)
    allow_cache	    = models.CharField(max_length=5)
    target_duration = models.CharField(max_length=5)

    def __unicode__(self):
        return self.filename

class Config(models.Model):
    enabled     = models.BooleanField()
    tokenurl    = models.CharField(max_length=255)
    cdnurl      = models.CharField(max_length=1024)
    cdnpattern  = models.CharField(max_length=255)
    tbx_api_key = models.CharField(max_length=100)
    secret	= models.BooleanField()
    gatra_enabled = models.BooleanField()
    gatra_url   = models.CharField(max_length=200)

class CdnSecret(models.Model):
    enabled	= models.BooleanField()
    gen		= models.CharField(max_length=1)
    key		= models.CharField(max_length=64)

    def __unicode__(self):
	return '%s:%s' % (self.gen, self.key)


class Token(models.Model):
    expiration  = models.DateTimeField()
    token	= models.CharField(max_length=255)
    video	= models.ForeignKey('Video')

    def __unicode__(self):
	return self.token

class Customer(models.Model):

    TYPE = ( ('half', 'half'),
	 ('mixed', 'mixed'),
	 ('full', 'full'),
	 ('full_payment', 'full_payment'),
	 ('payment', 'payment'),
	)

    name	= models.CharField(max_length=50)
    idp_code    = models.CharField(max_length=20)
    access_type = models.CharField(max_length=50, choices=TYPE)
    api_key     = models.CharField(max_length=50)

    def __unicode__(self):
	return self.name

