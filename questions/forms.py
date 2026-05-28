from django import forms
from questions.models import Question, Answer




class AskForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('title', 'text', 'tags')

    widgets = {
        'title': forms.TextInput(attrs={'placeholder': 'Введите краткое название вопроса'}),
        'text': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Опишите вашу проблему как можно подробнее'}),
    }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Напишите ваш ответ здесь...',
            }),
        }




