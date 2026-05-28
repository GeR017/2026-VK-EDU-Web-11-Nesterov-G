from django.db import models
from django.db.models import Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import Now, Extract


class Tag(models.Model):
    title = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
    def __str__(self):
        return self.title


class QuestionManager(models.Manager):
    def new(self):
        return self.select_related('author').prefetch_related('tags').annotate(
            answers_count=Question.get_answers_count_expression(),
            like_count=Question.get_likes_count_expression()
        ).order_by('-creation_date')

    def hot(self):
        return self.select_related('author').prefetch_related('tags').annotate(
            like_count=Question.get_likes_count_expression(),
            hot_score=Question.get_hot_score_expression()
        ).order_by('-hot_score', '-creation_date')

    def by_tag(self, tag_name):
        return self.filter(tags__title=tag_name).select_related('author').prefetch_related('tags').annotate(
            answers_count=Question.get_answers_count_expression(),
            like_count=Question.get_likes_count_expression()
        ).order_by('-creation_date')

    def get_detailed(self, question_id):
        return self.select_related('author').prefetch_related('tags').annotate(
            like_count=Question.get_likes_count_expression()
        ).filter(pk=question_id)

class AnswerManager(models.Manager):
    def for_question(self, question_id):
        return self.filter(question_id=question_id).select_related('author').order_by('-creation_date')

class Question(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Заголовок вопроса", max_length=255)
    text = models.TextField(verbose_name="Текст вопроса",max_length=5000)
    creation_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag')


    objects = QuestionManager()
    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def get_answers_count(self):
        return self.answer_set.count()

    def get_likes_count(self):
        return self.questionlike_set.count()

    @staticmethod
    def get_answers_count_expression():
        """Возвращает выражение для подсчета количества ответов"""
        return Count('answer', distinct=True)

    @staticmethod
    def get_likes_count_expression():
        return Count('questionlike', distinct=True)

    @staticmethod
    def get_hot_score_expression():
        age_in_hours = ExpressionWrapper(
            Extract(Now() - F('creation_date'), 'epoch') / 3600.0,
            output_field=FloatField()
        )
        return F('like_count') / (age_in_hours + 2) ** 1.8


    def __str__(self):
        return f"Вопрос #{self.id}: {self.title}"


class Answer(models.Model):
    objects = AnswerManager()
    
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Текст ответа",max_length=5000)
    creation_date = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(verbose_name="Корректный ответ?", default=False)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return f"Ответ #{self.id} на вопрос '{self.question.title}' от {self.author.username}"

    def get_likes_count(self):
        return self.answerlike_set.count()

class QuestionLike(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Лайк вопроса"
        verbose_name_plural = "Лайки вопросов"

        unique_together = [('user', 'question')]

    def __str__(self):
        return f"Лайк от {self.user.username} на вопрос {self.question.title}"


class AnswerLike(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Лайк ответа"
        verbose_name_plural = "Лайки ответов"

        unique_together = ('user', 'answer')

    def __str__(self):
        return f"Лайк от {self.user.username} for answer ID {self.answer.id}"
