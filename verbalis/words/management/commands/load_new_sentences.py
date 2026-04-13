import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from words.models import Sentence, Word


class Command(BaseCommand):
    help = 'Загружает из sentences_new.json предложения, которых ещё нет в БД (по PK)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixture',
            default=None,
            help='Путь к sentences_new.json (по умолчанию ищет в корне проекта)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать количество новых предложений без реальной загрузки',
        )

    def handle(self, *args, **options):
        fixture_path = options['fixture']
        if fixture_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )))
            fixture_path = os.path.join(base_dir, 'sentences_new.json')

        if not os.path.exists(fixture_path):
            self.stderr.write(self.style.ERROR(f'Файл не найден: {fixture_path}'))
            return

        self.stdout.write('Читаем файл...')
        with open(fixture_path, encoding='utf-8') as f:
            data = json.load(f)

        fixture_sentences = {
            entry['pk']: entry['fields']
            for entry in data
            if entry.get('model') == 'words.sentence'
        }
        self.stdout.write(f'В файле: {len(fixture_sentences)} предложений')

        existing_sentence_pks = set(Sentence.objects.values_list('pk', flat=True))
        self.stdout.write(f'В БД: {len(existing_sentence_pks)} предложений')

        new_entries = {
            pk: fields
            for pk, fields in fixture_sentences.items()
            if pk not in existing_sentence_pks
        }
        self.stdout.write(f'Новых предложений для добавления: {len(new_entries)}')

        if not new_entries:
            self.stdout.write(self.style.SUCCESS('Нечего добавлять — все предложения уже есть в БД.'))
            return

        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f'[dry-run] Будет добавлено {len(new_entries)} предложений.'))
            for pk, fields in list(new_entries.items())[:10]:
                self.stdout.write(f'  pk={pk} words={fields["words"]} "{fields["sentence"][:80]}"')
            if len(new_entries) > 10:
                self.stdout.write(f'  ... и ещё {len(new_entries) - 10}')
            return

        # Загружаем все существующие word PK — чтобы не сломать M2M на несуществующих словах
        self.stdout.write('Загружаем существующие PK слов...')
        existing_word_pks = set(Word.objects.values_list('pk', flat=True))

        # Шаг 1: создаём сами предложения (без M2M)
        self.stdout.write('Создаём предложения...')
        sentences_to_create = [
            Sentence(pk=pk, sentence=fields['sentence'])
            for pk, fields in new_entries.items()
        ]

        with transaction.atomic():
            Sentence.objects.bulk_create(sentences_to_create, batch_size=500)

            # Шаг 2: строим M2M-связи через промежуточную таблицу
            self.stdout.write('Добавляем M2M-связи со словами...')
            SentenceWord = Sentence.words.through  # авто-таблица words_sentence_words

            m2m_to_create = []
            skipped_word_refs = 0

            for pk, fields in new_entries.items():
                for word_pk in fields['words']:
                    if word_pk in existing_word_pks:
                        m2m_to_create.append(
                            SentenceWord(sentence_id=pk, word_id=word_pk)
                        )
                    else:
                        skipped_word_refs += 1

            SentenceWord.objects.bulk_create(m2m_to_create, batch_size=1000)

        self.stdout.write(self.style.SUCCESS(
            f'Добавлено {len(sentences_to_create)} предложений, '
            f'{len(m2m_to_create)} M2M-связей.'
        ))
        if skipped_word_refs:
            self.stdout.write(self.style.WARNING(
                f'Пропущено {skipped_word_refs} ссылок на слова, которых нет в БД. '
                f'Сначала запустите load_new_words, затем повторите загрузку предложений.'
            ))
