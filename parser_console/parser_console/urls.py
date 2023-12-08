from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls)
]


# Redirect to admin-panel from any url
urlpatterns += [
    re_path(r'^.*$', RedirectView.as_view(url='/admin/', permanent=False))
]
