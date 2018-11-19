"""epic_viz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls.static import static

from epic_viz import settings
from epic_viz import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.render_home, name='home'),
    url(r'^home/$', views.return_all_tags, name='ajax_home'),
    url(r'^search/$', views.return_search_tags, name='search'),
    url(r'^me/$', views.return_me, name='me_output'),
    url(r'^csv/$', views.return_csv, name='save_csv'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
