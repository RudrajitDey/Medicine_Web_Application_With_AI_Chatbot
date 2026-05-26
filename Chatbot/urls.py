from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.chatbot, name='chatbot'),
    path('api/sessions/', views.list_sessions, name='chat_sessions_list'),
    path('api/sessions/<int:session_id>/', views.get_session, name='chat_session_detail'),
    path('api/sessions/<int:session_id>/delete/', views.delete_session, name='chat_session_delete'),
    path('api/send/', views.send_message, name='chat_send_message'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
