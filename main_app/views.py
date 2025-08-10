from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect
from openai import OpenAI
from dotenv import load_dotenv
from .models import Victorina, Question, Answer, Stata
from user_app.models import MyUser
from django.http import JsonResponse
from user_app.forms import LoginForm
from django.contrib import auth
import json
from django.db.models import Count, OuterRef, Subquery, Max
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from main_app.forms import QuizForm, QuestionWithAnswersForm

load_dotenv()


# аутентификация
class IndexView(TemplateView):
    template_name = "main_app/index.html"
    
    def get(self, request, *args, **kwargs):
        login_form = LoginForm()
        context = {"login_form": login_form}
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        login_form = LoginForm(data=request.POST)
    
        if login_form.is_valid():
            username = request.POST.get("username")
            
            password = request.POST.get("password")
            
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return redirect('/')
            
        context = {"login_form": login_form}
        return self.render_to_response(context)

def quiz_view(request):
    query = request.GET.get("query")
    try:
        del request.session["id_quiz"]
        del request.session["number"]
        del request.session["i"]
        del request.session["questions"]
        del request.session["query"]
        del request.session["data_list"]
    except KeyError: 
        pass

    if query:
        victorins = Victorina.objects.filter(topic__contains=query)
    else:
        victorins = Victorina.objects.all()
    # print(victorins)
    
    # print(MyUser.objects.annotate(num_vict=Count('victorins')).order_by('-num_vict'))
    
    

    # user_stata = Stata.objects.filter(user=request.user).order_by('victorina', '-result')

    user_stata = (
        Stata.objects
            .filter(user=request.user)
            .values('victorina', 'victorina__topic')   # группируем по викторине
            .annotate(best_result=Max('result'))       # максимум внутри группы
            
            .order_by('victorina')
        )
    # print(user_stata)


    best_score = Stata.objects.filter(user=request.user, victorina=OuterRef('victorina')).order_by('-result').values('id')[:1]

    user_stata = Stata.objects.filter(user=request.user).filter(id=Subquery(best_score))
    print(user_stata)

    # user_test = Stata.objects.filter(user=OuterRef(request.user), victorina=OuterRef('victorina')).order_by('-result')
    # user_stata = Stata.objects.annotate(best_score=Subquery(user_test.values('result')[:1]))
    
    context = {"victorins": victorins, "query": query, "user_stata": user_stata}  
    return render(request, "main_app/all_quizes.html", context)
    


def explain(request):
    query_explain = request.GET.get("query_explain")
    if not query_explain:
        return render(request, "main_app/explain.html")

    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "developer",
                "content": """Объясни челоку значение какого выражения или слова, используй фразу 'так называемый' """,
            },
            {"role": "user", "content": query_explain},
        ],
    )

    answer = completion.choices[0].message.content
    print(answer)

    context = {"answer": answer}
    return render(request, "main_app/explain.html", context)


def gpt_proc(request):
    query = request.GET.get("query")
    answer = request.GET.get("answer")
    q_number = request.GET.get("q_number")
    if not query and not answer: #вывод вопрос с номером q_number (сама викторина)
        q_number = int(q_number)
        dic = request.session["questions"]
        context = {"question": dic[q_number], "q_number": q_number + 1}
        if len(request.session["data_list"]) > q_number:
            if request.session["data_list"][q_number]:
                context["answer_from_ses"] = request.session["data_list"][q_number]
        return render(request, "main_app/quiz_question.html", context)
    elif query: #первый запрос, создает викторину
        client = OpenAI()
        i = 5
        #request.session["j"] = i
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "developer",
                    "content": f"""Создай викторину на основе вопроса пользователя
                    Дай ответ в формате JSON, ключ question вопрос, answers список с ответами  Сгенерируй 4 варианта ответа.
                    Иногда, один из них может быть абсурдным, надо делать этот вариант ответа максимально уместным в контексте остальных вариантов но при этом явно маргинальным, глупым. Один ответ из всех 20, должен иметь незаметную отссылку на фильм "Джанго Освобожденный"
                    correct_answer с правильныи ответом. Викторина должна быть {i} вопросов."""
                    + """[{"question":"Вопрос1", "answers":["ответ1","ответ2","ответ3","ответ4"], "correct answer":"правильный ответ"},{}]. Не надо ```json """,
                },
                {"role": "user", "content": query},
            ],
        )

        answer = completion.choices[0].message.content
        dic = json.loads(answer)
        request.session["data_list"] = []
        request.session["questions"] = dic
        request.session["number"] = len(dic)
        request.session["query"] = query
        request.session["i"] = 0
    elif answer: #когда новый вопрос есть, а чел не выбрал ответ, потом снова к if not 
        dic = request.session["questions"]
        i = int(q_number) - 1
        question = dic[i]
        answer_dict = {
            "question": question["question"],
            "user_answer": answer,
            "correct_answer": question["correct_answer"],
        }
        if len(request.session["data_list"]) == i:
            request.session["data_list"].append(answer_dict)
        else:
            request.session["data_list"][i] = answer_dict
        print(request.session["data_list"])
        if i < request.session["number"] - 1:
            request.session["i"] = i + 1
        else:
            request.session["i"] = i + 1
            return redirect("/quiz_result")

    return redirect(f"/gpt_proc?q_number={request.session['i']}")


def quiz_question(request):
    return render(request, "main_app/quiz_question.html")


def quiz_result(request):
    data_list = request.session["data_list"]
    print(data_list)
    correct = 0
    for question in data_list:
        print(question)
        if question["user_answer"] == question["correct_answer"]:
            correct += 1
    context = {
        "correct": correct,
        "data_list": data_list,
        "number": request.session["number"],
    }
    if not request.session.get('id_quiz'): #создана гпт 
        context['j'] = request.session['number']
    else: #если загруженная
        vict = Victorina.objects.get(id=request.session['id_quiz'])
        stata = Stata.objects.create(user=request.user, victorina=vict, result=correct)
        context['j'] = vict.num_of_que
        stata.save()    
    request.session['correct'] = correct
    return render(request, "main_app/quiz_result.html", context)


def get_quiz(request, id_quiz):
    victorina = Victorina.objects.get(id=id_quiz)
    questions_list = Question.objects.filter(victorina=victorina)

    print(victorina)
    print(questions_list)
    dic = []

    for question in questions_list:
        answers_list = Answer.objects.filter(question=question)
        ans_list = []
        for answer in answers_list:
            ans_list.append(answer.text)
            if answer.correctable:
                correct_answer = answer.text

        print(ans_list)
        quest_dic = {
            "question": question.text,
            "answers": ans_list,
            "correct_answer": correct_answer,
        }
        dic.append(quest_dic)

        """ print(ans_list)
        quest_dic = {'question': question.text, 'answers': ans_list, 'correct_answer': correct_answer}
        dic.append(quest_dic) """

    request.session["data_list"] = []
    request.session["questions"] = dic
    print(dic)
    request.session["number"] = len(dic)
    request.session["i"] = 0
    request.session['id_quiz'] = id_quiz
    return redirect(f"/gpt_proc?q_number={request.session['i']}")


def save_quiz_to_bd(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"message": "нн иди авторизируйся бро"}, status=401)
        quest_list = request.session["questions"]
        topic = request.session["query"]
        vict = Victorina.objects.create(topic=topic, num_of_que=5, author=request.user)
        vict.save()
        stata = Stata.objects.create(user=request.user, victorina=vict, result=request.session['correct'])
        stata.save()
        for question in quest_list:
            quest_obj = Question.objects.create(
                victorina=vict, text=question["question"]
            )
            quest_obj.save()
            answ_list = question["answers"]
            for answer in answ_list:
                correctable = 1 if question["correct_answer"] == answer else 0
                answ_obj = Answer.objects.create(
                    correctable=correctable, question=quest_obj, text=answer
                )
                answ_obj.save()

        return JsonResponse(
            {"message": "Викторина успешно сохранена. Все четко"}, status=201
        )

    except Exception as e: 
        print(e)
        return JsonResponse({"error": "alert"}, status=400)
    # request.session.clear()
    
def edit_quiz(request, id_quiz):
    victorina = Victorina.objects.get(id=id_quiz)
    questions_list = Question.objects.filter(victorina=victorina)
    
    lst = []

    for question in questions_list:
        answers_list = Answer.objects.filter(question=question)
        print(answers_list[0])
        quest_dic = {
            "question": question,
            "answers": list(enumerate(answers_list))
        }
        lst.append(quest_dic)
    print(lst)
    print(list(enumerate(lst)))
    context = {'victorina': victorina, 'question_list': list(enumerate(lst))}

    return render(request, 'main_app/edit_quiz.html', context)


def edit_quiz_support(request):
    quiz_id = request.POST.get('quiz_id')
    print(quiz_id)
    victorina = Victorina.objects.get(id=quiz_id)
    topic = request.POST.get('topic') 
    victorina.topic = topic
    victorina.save()

    for n in range(5):
            question_id = request.POST.get(f'question_id{n}')
            question_text = request.POST.get(f'quest{n}')
            question = Question.objects.get(id=question_id)
            question.text = question_text
            question.save()

            for i in range(4):
                answer_id = request.POST.get(f'answer_id{n}_{i}')
                answer_text = request.POST.get(f'answer{n}_{i}')
                print(question, answer_text)
                answer = Answer.objects.get(id=answer_id)
                answer.text = answer_text
                answer.save()
    return redirect("/quiz/")
    # return HttpResponseRedirect(request.META['HTTP_REFERER'])


class CreateQuizView(CreateView):
    template_name = 'main_app/create_quiz.html'
    model = Victorina
    form_class = QuizForm
    
    def get(self, request, *args, **kwargs):
        quiz_form = QuizForm()
        question_form_set = []
        for i in range(5):
            question_form = QuestionWithAnswersForm(prefix=f'q{i}')
            question_form_set.append(question_form)
        return render(request, self.template_name, context={'quiz_form': quiz_form, 'question_form_set': question_form_set})
    
def create_quiz(request):
    pass 


def create_quiz_support(request):
    pass