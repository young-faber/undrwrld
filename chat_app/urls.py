from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from chat_app.views import (
    chat_view,
    message_list
)

urlpatterns = [
    path("chat/", chat_view, name="chat"), 
    path("message_list", message_list)
]


