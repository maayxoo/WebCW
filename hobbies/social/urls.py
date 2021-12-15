from django.urls import path, include

from social import views, viewsets, api

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('profiles', viewsets.ProfileViewSet)

app_name = 'social'

urlpatterns = [
    path('', views.messages_vue, name='messages'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('members/', views.members, name='members'),
    path('friends/', views.friends, name='friends'),
    path('profile/', views.profile, name='profile'),
    path('hobbies/', views.hobby_view, name='hobbies'),
    path('uploadimage/', views.upload_image, name='uploadimage'),
    path('api/messages/', api.messages_api, name='messages api'),
    path('api/messages/<int:message_id>/', api.message_api, name='message api'),
    path('rest-api/', include(router.urls)),
]
