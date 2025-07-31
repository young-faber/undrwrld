from django.shortcuts import render
from django.http import JsonResponse
from chat_app.models import Message
from django.core import serializers

import json

def chat_view(request):  
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message')
        print("Пришло сообщение:", message)

        Message.objects.create(text=message, user=request.user)

        return JsonResponse({'status': 'ok', 'message': message})
    return JsonResponse({'error': 'only POST allowed'}, status=405)


def message_list(request):
    if request.method == "GET":
        messages = Message.objects.all().order_by("-id")[:50]
        data = [{"user": m.user.username, "text": m.text} for m in messages]
        return JsonResponse({"messages": data})
    return JsonResponse({"error": "Only GET allowed"}, status=405)