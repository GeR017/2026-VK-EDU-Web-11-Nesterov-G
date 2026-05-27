from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Question, Answer, Tag

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

    paginator = Paginator(answer_list, 10)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    return render(request, 'questions/question.html', {
        'question': item,
        'answers': page_obj,
        'page_obj': page_obj,
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

#@login_required
def ask(request):
    return render(request, 'questions/ask.html')
