from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.conf import settings
import os
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('countries.urls')),

    # Add this for direct image access in development
    path('cache/<path:path>', serve, {'document_root': os.path.join(settings.BASE_DIR, 'cache')}),

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

