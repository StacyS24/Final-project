from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.signup, name='sign-up'), 
    path('organisation-sign-up/', views.organisationSignUp, name='organisation-sign-up'), 
    path('volunteer-sign-up/', views.volunteerSignUp, name='volunteer-sign-up'), 
    path('volunteer-profile/', views.volunteerProfile, name='volunteer-profile'), 
    path('organisation-profile/', views.organisationProfile, name='organisation-profile'),
    path('login/', views.login_view, name='login'),
    path('edit-volunteer-profile', views.editVolunteerProfile, name='edit-volunteer-profile'),
    path('upload-profile-picture/', views.upload_profile_picture, name='upload-profile-picture'),
    path('edit-organisation-profile', views.editOrganisationProfile, name='edit-organisation-profile'),
    path('log-out', views.logout, name='log-out'),
    path('home', views.home, name='home'),
    path('post-volunteer-oppourtunity', views.postVolunteerOpportunity, name='post-volunteer-oppourtunity'),
    path('opportunity/<int:opportunity_id>/save/', views.save_opportunity, name='save-opportunity'),
    path('opportunity/<int:opportunity_id>/apply/', views.apply_opportunity, name='apply-opportunity'),
    path('opportunity/<int:opportunity_id>/delete/', views.delete_opportunity, name='delete-opportunity'),
    path('opportunity/<int:opportunity_id>/', views.opportunity_detail, name='opportunity-detail'),
    path('all-oppourtunities/', views.all_oppourtunities, name='all_oppourtunities'),
    path('urgent-oppourtunities/', views.urgent_opportunties, name='urgent_opportunities'),
    path('testimonials/', views.testimonial_list, name='testimonial_list'),  
    path('testimonial-detail/<int:testimonial_id>', views.testimonial_detail, name='testimonial_detail'), 
    path('testimonials/submit/', views.submit_testimonial, name='submit_testimonial'),
    path('add-comment/<int:testimonial_id>', views.add_comment, name='add-comment'),
    path('testimonial/<int:testimonial_id>/like/', views.like_testimonial, name='like_testimonial'),
    path('testimonial/<int:testimonial_id>/report/', views.report_testimonial, name='report_testimonial'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('search_users', views.search_users, name='search_users'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('send_message/<int:recipient_id>', views.send_message, name='send_message'),
    path('view_messages/', views.view_messages, name='view_messages'),
    path('chat/<int:sender_id>/', views.chat_with_sender, name='chat_with_sender'),
    path('confirm_volunteer/<int:application_id>/', views.confirm_volunteer, name='confirm_volunteer'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)