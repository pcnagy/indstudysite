from django.urls import path
from . import views

urlpatterns=[
    path("", views.present, name="present"),
]