from django.urls import path
from . import views

urlpatterns=[
    path("", views.stocks, name="stocks"),
    path("<str:ticker>/", views.stock_detail, name="stock_detail")
]