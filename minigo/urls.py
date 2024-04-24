from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('', views.dashboard_section_view, name='home'),
    path('update-status/', views.update_status, name='update-status'),
    path('get-custom-search/', views.get_custom_search, name='get-custom-search'),
    path('campaign/', views.create_campaign_section_view, name='campaign'),


    
]