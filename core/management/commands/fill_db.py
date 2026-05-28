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
        # Локальный генератор для латинских слагов тегов
        fake_latin = Faker()
        password = make_password('password123')
        BATCH_SIZE = 2000

        with transaction.atomic():
            # 1. Создание Пользователей
            users_to_create = []
            for i in range(ratio):
                users_to_create.append(User(
                    username=f'{fake.user_name()}_{i}',
                    email=f'{fake.user_name()}_{i}@example.com',  # Исправлен формат email
                    password=password
                ))

            # bulk_create возвращает объекты с заполненными ID (для PostgreSQL)
            created_users = []
            for i in range(0, len(users_to_create), BATCH_SIZE):
                created_users.extend(User.objects.bulk_create(users_to_create[i:i + BATCH_SIZE]))

            user_ids = [u.id for u in created_users]
            user_min_id, user_max_id = min(user_ids), max(user_ids)

            # 2. Создание Профилей
            profiles_to_create = [Profile(user_id=u_id) for u_id in user_ids]
            for i in range(0, len(profiles_to_create), BATCH_SIZE):
                Profile.objects.bulk_create(profiles_to_create[i:i + BATCH_SIZE])

            # 3. Создание Тегов
            tags_to_create = []
            for i in range(ratio):
                # Используем латинские слова для SlugField, чтобы избежать проблем с кириллицей
                tags_to_create.append(Tag(title=f'{fake_latin.word()}_{i}'))

            created_tags = []
            for i in range(0, len(tags_to_create), BATCH_SIZE):
                created_tags.extend(Tag.objects.bulk_create(tags_to_create[i:i + BATCH_SIZE], ignore_conflicts=False))

            tag_ids = [t.id for t in created_tags if t.id is not None]
            tag_min_id, tag_max_id = min(tag_ids), max(tag_ids)

            # 4. Создание Вопросов
            questions_to_create = []
            num_questions = ratio * 10
            for _ in range(num_questions):
                questions_to_create.append(Question(
                    author_id=random.randint(user_min_id, user_max_id),
                    title=fake.sentence(nb_words=6)[:255],
                    text=fake.text(max_nb_chars=500),
                ))

            created_questions = []
            for i in range(0, len(questions_to_create), BATCH_SIZE):
                created_questions.extend(Question.objects.bulk_create(questions_to_create[i:i + BATCH_SIZE]))

            question_ids = [q.id for q in created_questions]
            question_min_id, question_max_id = min(question_ids), max(question_ids)

            # 5. Создание связей Вопросы-Теги (M2M через промежуточную таблицу)
            ThroughModel = Question.tags.through
            question_tags = []
            for question_id in question_ids:
                num_tags = random.randint(1, 3)
                chosen_tags = random.sample(range(tag_min_id, tag_max_id + 1), k=num_tags)
                for tag_id in chosen_tags:
                    question_tags.append(ThroughModel(question_id=question_id, tag_id=tag_id))

            for i in range(0, len(question_tags), BATCH_SIZE):
                ThroughModel.objects.bulk_create(question_tags[i:i + BATCH_SIZE], ignore_conflicts=True)

            # 6. Создание Ответов
            answers_to_create = []
            num_answers = ratio * 100
            for _ in range(num_answers):
                answers_to_create.append(Answer(
                    author_id=random.randint(user_min_id, user_max_id),
                    question_id=random.randint(question_min_id, question_max_id),
                    text=fake.text(max_nb_chars=500)
                ))

            created_answers = []
            for i in range(0, len(answers_to_create), BATCH_SIZE):
                created_answers.extend(Answer.objects.bulk_create(answers_to_create[i:i + BATCH_SIZE]))

            answer_ids = [a.id for a in created_answers]
            answer_min_id, answer_max_id = min(answer_ids), max(answer_ids)

            # 7. Создание Лайков к Вопросам
            num_question_likes = ratio * 100
            question_likes = []
            for _ in range(num_question_likes):
                question_likes.append(QuestionLike(
                    user_id=random.randint(user_min_id, user_max_id),
                    question_id=random.randint(question_min_id, question_max_id)
                ))

            for i in range(0, len(question_likes), BATCH_SIZE):
                QuestionLike.objects.bulk_create(question_likes[i:i + BATCH_SIZE], ignore_conflicts=True)

            # 8. Создание Лайков к Ответам
            num_answer_likes = ratio * 100
            answer_likes = []
            for _ in range(num_answer_likes):
                answer_likes.append(AnswerLike(
                    user_id=random.randint(user_min_id, user_max_id),
                    answer_id=random.randint(answer_min_id, answer_max_id)
                ))

            for i in range(0, len(answer_likes), BATCH_SIZE):
                AnswerLike.objects.bulk_create(answer_likes[i:i + BATCH_SIZE], ignore_conflicts=True)

