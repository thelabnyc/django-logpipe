from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = (
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),
)
