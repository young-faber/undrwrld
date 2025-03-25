from django.shortcuts import render, HttpResponse
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

# Create your views here.
def index(request):
    return render(request, "main_app/index.html")

def quiz_view(request):
    return render(request, "main_app/all_quizes.html")

def explain(request):
    return render(request, 'main_app/explain.html')

def gpt_proc(request):
    query = request.GET.get('query')
    
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "developer",
                "content": '''Создай викторину на основе вопроса пользователя. 
Дай ответ в формате JSON, ключ question вопрос, answers список с ответами  Сгенерируй 4 варианта ответа. 
correct_answer с правильныи ответом. Викторина должна быть не меньше 5 вопросов. 
[{"question":"Вопрос1", "answers":["ответ1","ответ2","ответ3","ответ4"], "correct answer":"правильный ответ"},{}]. Не надо ```json'''
            },
            {
                "role": "user",
                "content": query
            }
        ]
    )

    answer = completion.choices[0].message.content
    print(answer)
    dic = json.loads(answer)
    context = {'answer':answer, 'questions':dic, 'npage':1}
    request.session['questions'] = dic
    return render(request, "main_app/quiz_question.html", context)

def gpt_proc_explain(request):
    query_explain = request.GET.get('query_explain')
    
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "developer",
                "content": '''Объясни челоку значение какого выражения или слова'''
            },
            {
                "role": "user",
                "content": query_explain
            }
        ]
    )

    answer = completion.choices[0].message.content
    print(answer)
    
    context = {'answer':answer}
    return render(request, "main_app/explain.html", context)


def quiz_question(request):
    return render(request, 'main_app/quiz_question.html')