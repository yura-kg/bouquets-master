from django.urls import path
from . import views

urlpatterns = [
    path('', views.bouquet_list, name='bouquet_list'),
    path('create/', views.create_bouquet, name='create_bouquet'),
    path('edit/<int:pk>/', views.edit_bouquet, name='edit_bouquet'),
    path('delete/<int:pk>/', views.delete_bouquet, name='delete_bouquet'),
    path('add-composition/<int:bouquet_pk>/', views.add_composition_item, name='add_composition_item'),
    path('remove-composition/<int:bouquet_pk>/<int:item_pk>/', views.remove_composition_item, name='remove_composition_item'),
    path('search-flowers/', views.search_flowers_for_bouquet, name='search_flowers_for_bouquet'),
    path('import-tilda/', views.import_tilda_csv, name='import_tilda_csv'),
    path('export-tilda/', views.export_tilda_csv, name='export_tilda_csv'),
]
