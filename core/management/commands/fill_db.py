import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from questions.models import Question, Answer, Tag, Profile, QuestionLike, AnswerLike
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

        users = []
        for i in range(1, ratio + 1):
            users.append(User(username=fake.user_name(), email=fake.email(), password=password))
            if len(users) % BATCH_SIZE == 0:
                User.objects.bulk_create(users)
                users = []
        if users:
            User.objects.bulk_create(users)

        user_ids = list(User.objects.order_by('-id').values_list('id', flat=True)[:ratio])
        user_ids.reverse()

        # Сразу создаем для них Profile (Связь OneToOne), чтобы не нарушать логику
        profiles_to_create = [Profile(user_id=u_id) for u_id in user_ids]
        for i in range(0, len(profiles_to_create), BATCH_SIZE):
            Profile.objects.bulk_create(profiles_to_create[i:i + BATCH_SIZE])


        tags = []
        for i in range(1, ratio + 1):
            tags.append(Tag(title=f'{fake.domain_word()} {i}'))
        Tag.objects.bulk_create(tags, batch_size=BATCH_SIZE)
        tag_ids = list(Tag.objects.values_list('id', flat=True))

        questions = []
        num_questions = ratio * 10
        for i in range(1, num_questions + 1):
            questions.append(Question(
                author_id=random.choice(user_ids),
                title=fake.sentence(),
                text=fake.text(max_nb_chars=500),
            ))
            if len(questions) % BATCH_SIZE == 0:
                Question.objects.bulk_create(questions)
                questions = []
        if questions:
            Question.objects.bulk_create(questions)
        question_ids = list(Question.objects.values_list('id', flat=True))

        ThroughModel = Question.tags.through
        question_tags = []
        for i, question_id in enumerate(question_ids):
            tags_for_question = random.sample(tag_ids, k=random.randint(1, 3))
            for tag_id in tags_for_question:
                question_tags.append(ThroughModel(question_id=question_id, tag_id=tag_id))
            if len(question_tags) % BATCH_SIZE == 0:
                ThroughModel.objects.bulk_create(question_tags, ignore_conflicts=True)
                question_tags = []
        if question_tags:
            ThroughModel.objects.bulk_create(question_tags, ignore_conflicts=True)

        answers = []
        num_answers = ratio * 100
        for i in range(1, num_answers + 1):
            answers.append(Answer(
                author_id=random.choice(user_ids),
                question_id=random.choice(question_ids),
                text=fake.text(max_nb_chars=500)
            ))
            if len(answers) % BATCH_SIZE == 0:
                Answer.objects.bulk_create(answers)
                answers = []
        if answers:
            Answer.objects.bulk_create(answers)
        answer_ids = list(Answer.objects.values_list('id', flat=True))


        num_question_likes = ratio * 100
        num_answer_likes = ratio * 100


        question_likes_gen = (QuestionLike(user_id=random.choice(user_ids), question_id=random.choice(question_ids)) for _ in range(num_question_likes))
        QuestionLike.objects.bulk_create(question_likes_gen, batch_size=BATCH_SIZE, ignore_conflicts=True)

        answer_likes_gen = (AnswerLike(user_id=random.choice(user_ids), answer_id=random.choice(answer_ids)) for _ in range(num_answer_likes))
        AnswerLike.objects.bulk_create(answer_likes_gen, batch_size=BATCH_SIZE, ignore_conflicts=True)