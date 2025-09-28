from django.urls import path
from . import views

urlpatterns = [
    path('', views.flower_catalog, name='flower_catalog'),
    path('add/', views.add_flower_item, name='add_flower_item'),
    path('edit/<int:pk>/', views.edit_flower_item, name='edit_flower_item'),
    path('delete/<int:pk>/', views.delete_flower_item, name='delete_flower_item'),
    path('search/', views.search_flowers, name='search_flowers'),
    path('import-csv/', views.import_csv, name='import_csv'),
]
