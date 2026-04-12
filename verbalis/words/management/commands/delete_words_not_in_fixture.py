import json
import os
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from words.models import Word, UserWord
# from recommendations.models import ChosenWords, RecommendedWords, AcceptedRecs


class Command(BaseCommand):
    help = 'Удаляет записи Word, которых нет в words_filtered.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixture',
            default=None,
            help='Путь к words_filtered.json (по умолчанию ищет в корне проекта)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать, что будет удалено, без реального удаления',
        )

    def handle(self, *args, **options):
        fixture_path = options['fixture']
        if fixture_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )))
            fixture_path = os.path.join(base_dir, 'words_filtered.json')

        if not os.path.exists(fixture_path):
            self.stderr.write(self.style.ERROR(f'Файл не найден: {fixture_path}'))
            return

        with open(fixture_path, encoding='utf-8') as f:
            data = json.load(f)

        fixture_pks = {entry['pk'] for entry in data if entry.get('model') == 'words.word'}
        self.stdout.write(f'В файле: {len(fixture_pks)} слов')

        word_ids_to_delete = list(
            Word.objects.exclude(pk__in=fixture_pks).values_list('pk', flat=True)
        )
        count = len(word_ids_to_delete)

        if count == 0:
            self.stdout.write(self.style.SUCCESS('Нечего удалять — все слова в БД совпадают с файлом.'))
            return

        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f'[dry-run] Будет удалено {count} записей Word.'))
            words_sample = Word.objects.filter(pk__in=word_ids_to_delete[:50]).values_list('pk', 'word')
            for pk, word in words_sample:
                self.stdout.write(f'  pk={pk} "{word}"')
            if count > 50:
                self.stdout.write(f'  ... и ещё {count - 50}')
            return

        # SQLite: PRAGMA foreign_keys нельзя менять внутри транзакции,
        # поэтому отключаем до transaction.atomic()
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA foreign_keys = OFF')

        try:
            with transaction.atomic():
                # Удаляем зависимые таблицы через сырой SQL,
                # чтобы не зависеть от импортов конкретных моделей
                with connection.cursor() as cursor:
                    cursor.execute(
                        'DELETE FROM recommendations_chosenwords WHERE word_id IN %s'
                        % self._sql_ids(word_ids_to_delete)
                    )
                    cursor.execute(
                        'DELETE FROM recommendations_recommendedwords WHERE word_id IN %s'
                        % self._sql_ids(word_ids_to_delete)
                    )
                    cursor.execute(
                        'DELETE FROM recommendations_acceptedrecs WHERE word_id IN %s'
                        % self._sql_ids(word_ids_to_delete)
                    )

                d = UserWord.objects.filter(word_id__in=word_ids_to_delete).delete()
                self.stdout.write(f'  UserWord удалено: {d[0]}')

                deleted, _ = Word.objects.filter(pk__in=word_ids_to_delete).delete()
                self.stdout.write(self.style.SUCCESS(f'Удалено {deleted} записей Word.'))
        finally:
            with connection.cursor() as cursor:
                cursor.execute('PRAGMA foreign_keys = ON')

    @staticmethod
    def _sql_ids(ids):
        """Формирует строку вида (1,2,3) для подстановки в SQL IN."""
        return '(' + ','.join(str(i) for i in ids) + ')'
