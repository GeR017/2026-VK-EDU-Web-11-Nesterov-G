from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator


QUESTIONS = [
    {
        'id': i,
        'title': f'question title {i}',
        'text': f'Text {i}',
        'answers': [
            {'id': j, 'text': f'Answer {j}'}
             for j in range(5)
        ]
    }
    for i in range(30)
]


def index(request):
    page_num = request.GET.get('page', 1)

    paginator = Paginator(QUESTIONS, 5)

    page_obj = paginator.get_page(page_num)

    return render(request, 'questions/index.html', {
        'questions': page_obj,
        'page_obj': page_obj
    })


def hot(request):
    page_num = request.GET.get('page', 1)

    paginator = Paginator(QUESTIONS[::-1], 5)
    page_obj = paginator.get_page(page_num)

    return render(request, 'questions/hot.html', {
        'questions': page_obj,
        'page_obj': page_obj
    })

def question(request,question_id):
    item = next((q for q in QUESTIONS if q['id'] == question_id), None)

    if not item:
        return HttpResponse('question not found', status=404)

    return render(request, 'questions/question.html', {
        'question': item,
        'answers': item['answers'],
    })

def tag(request, tag_name):
    # В реальном приложении здесь будет фильтрация по тегу
    questions_for_tag = QUESTIONS[:10]
    page_num = request.GET.get('page', 1)
    paginator = Paginator(questions_for_tag, 5)
    page_obj = paginator.get_page(page_num)

    return render(request, 'questions/tag.html', {
        'tag': tag_name,
        'questions': page_obj,
        'page_obj': page_obj
    })

def ask(request):
    return render(request, 'questions/ask.html')