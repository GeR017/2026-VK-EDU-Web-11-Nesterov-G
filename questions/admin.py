from django.contrib import admin

from questions.models import Question, Answer, Tag, QuestionLike, AnswerLike
# Register your models here.

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "author", "creation_date"]
    list_filter = ["tags", "creation_date"]
    search_fields = ["title", "text", "author__username"]
    raw_id_fields = ["author"]

    class AnswerInline(admin.TabularInline):
        model = Answer
        fields = ["author", "text", "is_correct"]
        extra = 0
        raw_id_fields = ["author"]
    inlines = [AnswerInline]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "question"]
    raw_id_fields = ["author", "question"]
    search_fields = ["author__email", "author__username", "question__title"]
    list_filter = ["is_correct"]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'question']
    raw_id_fields = ['user', 'question']

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'answer']
    raw_id_fields = ['user', 'answer']
