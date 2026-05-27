from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .forms import AskForm, AnswerForm
from .models import Question, Answer, Tag
from django.urls import reverse, reverse_lazy

@login_required(login_url=reverse_lazy('core:login'))
def index(request):

    questions_list = Question.objects.new().prefetch_related("tags")
    paginator = Paginator(questions_list, 5)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    return render(request, 'questions/index.html', {
        'questions': page_obj,
        'page_obj': page_obj
    })

def hot(request):
    questions_list = Question.objects.hot().prefetch_related("tags")
    paginator = Paginator(questions_list, 5)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    return render(request, 'questions/hot.html', {
        'questions': page_obj,
        'page_obj': page_obj
    })

def question(request, question_id):
    item = get_object_or_404(Question.objects.get_detailed(question_id))
    answer_list = Answer.objects.for_question(question_id=question_id)


    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = item
            answer.author = request.user
            answer.save()

            base_url = reverse('question', args=[question_id])

            last_page = (answer_list.count() + 9)//10

            return HttpResponseRedirect(f"{base_url}?page={last_page}#answer-{answer.id}")

    else:
        form = AnswerForm()
        paginator = Paginator(answer_list, 10)
        page_num = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_num)

        return render(request, 'questions/question.html', {
            'question': item,
            'answers': page_obj,
            'page_obj': page_obj,
            'form' : form,
        })


def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, title=tag_name)
    questions_for_tag = Question.objects.by_tag(tag_name)

    paginator = Paginator(questions_for_tag, 5)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    return render(request, 'questions/tag.html', {
        'tag': tag_obj.title,  #
        'questions': page_obj,
        'page_obj': page_obj
    })

@login_required(login_url='login')
def ask(request):
    if request.method == "POST":
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)

            question.author = request.user
            question.save()

            form.save_m2m()
            return HttpResponseRedirect(question, id=question.id)
    else:
        form = AskForm()
    return render(request, 'questions/ask.html', {'form' : form})

