from django import forms
from main_app.models import Victorina, Question, Answer
from django.forms.models import inlineformset_factory

class QuizForm(forms.ModelForm):
    class Meta():
        model = Victorina
        fields = ['topic']

class QuestionForm(forms.ModelForm):
    class Meta():
        model = Question
        fields = ['text']

class AnswerForm(forms.ModelForm):
    class Meta():
        model = Answer
        fields = ['correctable', 'text']

QuestionFormSet = inlineformset_factory(Victorina, Question, QuestionForm, extra = 5)
AnswerFormSet = inlineformset_factory(Question, Answer, AnswerForm, extra=4)

class QuestionWithAnswersForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.get("prefix")
        if not self.prefix: 
            print('no prefix')
            return
        super().__init__(*args, **kwargs)
        self.answer_form_set = AnswerFormSet(instance=self.instance, prefix=f"{self.prefix}-answers")
        
    def is_valid(self):
        pass

    def save(self):
        pass

