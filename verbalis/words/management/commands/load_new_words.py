import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from words.models import Word


class Command(BaseCommand):
    help = 'Загружает из words_updated_filtered.json слова, которых ещё нет в БД (по PK)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixture',
            default=None,
            help='Путь к words_updated_filtered.json (по умолчанию ищет в корне проекта)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать количество новых слов без реальной загрузки',
        )

    def handle(self, *args, **options):
        fixture_path = options['fixture']
        if fixture_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )))
            fixture_path = os.path.join(base_dir, 'words_updated_filtered.json')

        if not os.path.exists(fixture_path):
            self.stderr.write(self.style.ERROR(f'Файл не найден: {fixture_path}'))
            return

        with open(fixture_path, encoding='utf-8') as f:
            data = json.load(f)

        fixture_words = {
            entry['pk']: entry['fields']
            for entry in data
            if entry.get('model') == 'words.word'
        }
        self.stdout.write(f'В файле: {len(fixture_words)} слов')

        existing_pks = set(Word.objects.values_list('pk', flat=True))
        self.stdout.write(f'В БД: {len(existing_pks)} слов')

        new_entries = {pk: fields for pk, fields in fixture_words.items() if pk not in existing_pks}
        self.stdout.write(f'Новых слов для добавления: {len(new_entries)}')

        if not new_entries:
            self.stdout.write(self.style.SUCCESS('Нечего добавлять — все слова уже есть в БД.'))
            return

        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f'[dry-run] Будет добавлено {len(new_entries)} слов.'))
            for pk, fields in list(new_entries.items())[:20]:
                self.stdout.write(f'  pk={pk} "{fields["word"]}" — {fields["word_translate"]}')
            if len(new_entries) > 20:
                self.stdout.write(f'  ... и ещё {len(new_entries) - 20}')
            return

        words_to_create = [
            Word(
                pk=pk,
                language_id=fields['language'],
                word=fields['word'],
                word_translate=fields['word_translate'],
                part_of_speach=fields['part_of_speach'],
            )
            for pk, fields in new_entries.items()
        ]

        with transaction.atomic():
            created = Word.objects.bulk_create(words_to_create, batch_size=500)

        self.stdout.write(self.style.SUCCESS(f'Добавлено {len(created)} новых слов.'))
