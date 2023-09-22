from django.urls import path
from . import views

urlpatterns = [
    path('', views.DatatableView.as_view(), name='datatable'),
    path('ajaxTable/', views.ajaxTable, name='ajaxTable'),
]