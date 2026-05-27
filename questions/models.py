from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import Now, Extract


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
    def __str__(self):
        return self.title


class QuestionManager(models.Manager):
    def new(self):
        return self.select_related('author') \
                   .prefetch_related('tags') \
                   .annotate(answers_count=Count('answer', distinct=True),
                             like_count=Count('questionlike', distinct=True)) \
                   .order_by('-creation_date')


    def hot(self):
        age_in_hours = ExpressionWrapper(
            Extract(Now() - F('creation_date'), 'epoch') / 3600.0,
            output_field=FloatField()
        )

        return self.select_related('author').annotate(
            like_count=Count('questionlike', distinct=True)
        ).annotate(
            hot_score=F('like_count') / (age_in_hours + 2) ** 1.8
        ).order_by('-hot_score')

    def by_tag(self, tag_name):
        return self.filter(tags__title=tag_name) \
                   .select_related('author') \
                   .prefetch_related('tags') \
                   .annotate(answers_count=Count('answer', distinct=True),
                             like_count=Count('questionlike', distinct=True)) \
                   .order_by('-creation_date')

    def get_detailed(self, question_id):
        return self.select_related('author') \
            .prefetch_related('tags') \
            .annotate(like_count=Count('questionlike', distinct=True)) \
            .filter(pk=question_id)
class AnswerManager(models.Manager):
    def for_question(self, question_id):
        return self.filter(question_id=question_id) \
                   .select_related('author') \
                   .annotate(likes_count=Count('answerlike', distinct=True)) \
                   .order_by('-creation_date')

class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Заголовок вопроса", max_length=255)
    text = models.TextField(verbose_name="Текст вопроса")
    creation_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)

    objects = QuestionManager()
    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


    def __str__(self):
        return f"Вопрос #{self.id}: {self.title}"


class Answer(models.Model):
    objects = AnswerManager()
    
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Текст ответа")
    creation_date = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(verbose_name="Корректный ответ?", default=False)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return f"Ответ #{self.id} на вопрос '{self.question.title}' от {self.author.username}"


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Лайк вопроса"
        verbose_name_plural = "Лайки вопросов"

        unique_together = [('user', 'question')]

    def __str__(self):
        return f"Лайк от {self.user.username} на вопрос {self.question.title}"


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Лайк ответа"
        verbose_name_plural = "Лайки ответов"

        unique_together = ('user', 'answer')

    def __str__(self):
        return f"Лайк от {self.user.username} for answer ID {self.answer.id}"
