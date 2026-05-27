import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from questions.models import Question, Answer, Tag, QuestionLike, AnswerLike
from core.models import Profile
from faker import Faker
from django.db import transaction


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--ratio', dest="ratio", type=int, required=True)

    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker('ru_RU')
        password = make_password('password123')
        BATCH_SIZE = 2000

        with transaction.atomic():

            users = []
            for i in range(ratio):
                users.append(User(username=f'{fake.user_name()}_{i}', email=f'{fake.unique.email()}_{i}', password=password))
                if len(users) % BATCH_SIZE == 0:
                    User.objects.bulk_create(users)
                    users = []
            if users:
                User.objects.bulk_create(users)

            last_users = User.objects.order_by('-id')[:ratio]
            user_ids = list(last_users.values_list('id', flat=True))
            user_min_id, user_max_id = min(user_ids), max(user_ids)

            profiles_to_create = [Profile(user_id=u_id) for u_id in user_ids]
            for i in range(0, len(profiles_to_create), BATCH_SIZE):
                Profile.objects.bulk_create(profiles_to_create[i:i + BATCH_SIZE])

            tags = []
            for i in range(ratio):
                tags.append(Tag(title=f'{fake.word()}_{i}'))
                if len(tags) % BATCH_SIZE == 0:
                    Tag.objects.bulk_create(tags, ignore_conflicts=True)
                    tags = []
            if tags:
                Tag.objects.bulk_create(tags, ignore_conflicts=True)

            tag_ids = list(Tag.objects.order_by('-id')[:ratio].values_list('id', flat=True))
            tag_min_id, tag_max_id = min(tag_ids), max(tag_ids)

            questions = []
            num_questions = ratio * 10
            for _ in range(num_questions):
                questions.append(Question(
                    author_id=random.randint(user_min_id, user_max_id),
                    title=fake.sentence(nb_words=6)[:255],
                    text=fake.text(max_nb_chars=500),
                ))
                if len(questions) % BATCH_SIZE == 0:
                    Question.objects.bulk_create(questions)
                    questions = []
            if questions:
                Question.objects.bulk_create(questions)

            created_questions = Question.objects.order_by('-id')[:num_questions]
            question_ids = list(created_questions.values_list('id', flat=True))
            question_min_id, question_max_id = min(question_ids), max(question_ids)

            ThroughModel = Question.tags.through
            question_tags = []
            for question_id in question_ids:
                num_tags = random.randint(1, 3)
                chosen_tags = random.sample(range(tag_min_id, tag_max_id + 1), k=num_tags)
                for tag_id in chosen_tags:
                    question_tags.append(ThroughModel(question_id=question_id, tag_id=tag_id))
                if len(question_tags) % BATCH_SIZE == 0:
                    ThroughModel.objects.bulk_create(question_tags, ignore_conflicts=True)
                    question_tags = []
            if question_tags:
                ThroughModel.objects.bulk_create(question_tags, ignore_conflicts=True)

            answers = []
            num_answers = ratio * 100
            for _ in range(num_answers):
                answers.append(Answer(
                    author_id=random.randint(user_min_id, user_max_id),
                    question_id=random.randint(question_min_id, question_max_id),
                    text=fake.text(max_nb_chars=500)
                ))
                if len(answers) % BATCH_SIZE == 0:
                    Answer.objects.bulk_create(answers)
                    answers = []
            if answers:
                Answer.objects.bulk_create(answers)

            created_answers = Answer.objects.order_by('-id')[:num_answers]
            answer_ids = list(created_answers.values_list('id', flat=True))
            answer_min_id, answer_max_id = min(answer_ids), max(answer_ids)

            num_question_likes = ratio * 100
            question_likes = []
            for _ in range(num_question_likes):
                question_likes.append(QuestionLike(
                    user_id=random.randint(user_min_id, user_max_id),
                    question_id=random.randint(question_min_id, question_max_id)
                ))
                if len(question_likes) % BATCH_SIZE == 0:
                    QuestionLike.objects.bulk_create(question_likes, ignore_conflicts=True)
                    question_likes = []
            if question_likes:
                QuestionLike.objects.bulk_create(question_likes, ignore_conflicts=True)

            num_answer_likes = ratio * 100
            answer_likes = []
            for _ in range(num_answer_likes):
                answer_likes.append(AnswerLike(
                    user_id=random.randint(user_min_id, user_max_id),
                    answer_id=random.randint(answer_min_id, answer_max_id)
                ))
                if len(answer_likes) % BATCH_SIZE == 0:
                    AnswerLike.objects.bulk_create(answer_likes, ignore_conflicts=True)
                    answer_likes = []
            if answer_likes:
                AnswerLike.objects.bulk_create(answer_likes, ignore_conflicts=True)
