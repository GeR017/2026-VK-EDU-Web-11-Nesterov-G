from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from questions import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot', views.hot, name='hot'),
    path('question/<int:question_id>', views.question, name='question'),
    path('tag/<str:tag_name>',views.tag,name='tag'),
    path('ask', views.ask, name='ask'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)