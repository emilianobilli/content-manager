"""content_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from video_manager.views import vm_GetRoot
from video_manager.views import vm_PostRoot
from video_manager.views import vm_Crossdomain
from video_manager.views import vm_PostVideo
from video_manager.views import vm_GetManifestByToken
from subs_manager.views  import sm_GetSub
from subs_manager.views  import sm_PostSub
from subs_manager.views  import sm_HPostSub
from subs_manager.views  import sm_UploadFile
#from subs_manager.views  import sm_add_subtitle_page
from subs_manager.views  import sm_home_subtitle_page
from cuepoints_manager.views import cm_PostCuePoint
from cuepoints_manager.views import cm_GetCuePoint

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^video/(?P<api_key>.+)/(?P<token_type>.+)/(?P<token>.+)/(?P<house_id>.+)/$',vm_GetRoot),
    url(r'^video/token/(?P<token>.+)/$', vm_GetManifestByToken),
    url(r'^video/checkauth/$',vm_PostRoot ),
    url(r'^video/add/$', vm_PostVideo),
    url(r'^subtitle/(?P<house_id>.+)/(?P<lang>.+)/(?P<format>.+)/(?P<ret>.+)/$', sm_GetSub),
    url(r'^subtitle/add/$', sm_HPostSub),
#    url(r'^subtitle/sub_form/$', sm_add_subtitle_page),
    url(r'^subtitle/upload/$', sm_UploadFile),
    url(r'^crossdomain.xml', vm_Crossdomain),
    url(r'^subtitle/home/$', sm_home_subtitle_page),
    url(r'^cuepoint/$', cm_PostCuePoint),
    url(r'^cuepoint/(?P<house_id>.+)/(?P<lang>.+)/(?P<format>.+)/(?P<ret>.+)/$', cm_GetCuePoint),
]
