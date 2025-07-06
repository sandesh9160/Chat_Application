from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat, name='chat'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('upload_attachment/', views.upload_attachment, name='upload_attachment'),
    path('download_attachment/<int:message_id>/', views.download_attachment, name='download_attachment'),
    path('attachment_preview/<int:message_id>/', views.attachment_preview, name='attachment_preview'),
    path('api/mentions/', views.mention_usernames, name='mention-usernames'),
    path('api/delete-message/<int:msg_id>/', views.delete_message, name='delete_message'),
]
