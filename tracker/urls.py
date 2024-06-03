from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('import_data', views.import_data, name="import_data"),
    path('generate_report', views.generate_report, name="generate_report"),
    path('generate_packet', views.generate_packet, name="generate_packet"),  # New path
]