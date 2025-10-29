from django.urls import path
from . import views

urlpatterns = [
    path('countries/image', views.countries_image, name='countries-image'),  
    path('countries/refresh', views.refresh_countries, name='refresh-countries'),
    path('countries', views.get_countries, name='get-countries'),
    path('countries/<str:name>', views.get_country_by_name, name='get-country-by-name'),
    path('countries/<str:name>/delete', views.delete_country, name='delete-country'),
    path('status', views.status_view, name='status'),
     
]