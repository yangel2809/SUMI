from django.contrib import admin
from django.urls import path, re_path, include  # add this
from django.conf import settings
from django.conf.urls.static import static

from apps.essays.views import *
from apps.home.views import *
from apps.sales.views import *
from apps.home.utils import *

urlpatterns = [
    path('admin/', admin.site.urls),         
    path("", include("apps.authentication.urls")),
    path("", include("apps.essays.urls")),
    path("", include("apps.home.urls")),
    path("", include("apps.sales.urls")),
    path("", include("apps.production.urls")),
    path("", include("apps.graphics.urls")),
    path("documents/", include("documents.urls")),
    re_path(r'^images/(?P<path>.*)$', protected_serve),#Protect image static files

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "apps.home.utils.page_400"
handler403 = "apps.home.utils.page_403"
handler404 = "apps.home.utils.page_404"
handler500 = "apps.home.utils.page_500"