"""
URL configuration for django_inception project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from main_app.views import (
    IndexView,
    quiz_view,
    gpt_proc,
    quiz_question,
    explain,
    quiz_result,
    get_quiz,
    save_quiz_to_bd,
    edit_quiz,
    edit_quiz_support,
    create_quiz_support,
    CreateQuizView
)

urlpatterns = [
    path("", IndexView.as_view()),
    path("quiz/", quiz_view),
    path("quiz/<int:id_quiz>", get_quiz),
    path("quiz/edit/<int:id_quiz>", edit_quiz),
    path("edit_quiz_support/", edit_quiz_support),
    path("create_quiz/", CreateQuizView.as_view()),
    path("create_quiz_support/", create_quiz_support),
    path("gpt_proc", gpt_proc),
    path("quiz_question", quiz_question),
    path("explain/", explain),
    path("quiz_result/", quiz_result),
    path("save_quiz_to_bd", save_quiz_to_bd),
]
