from django.views.generic import ListView
from django.shortcuts import render, redirect

import random

from words.models import Word
from languages.models import Language
from .models import Session, ChosenWords, AcceptedRecs, RecommendedWords
from .utils import get_recommendations_by_word_ids


class RandomWordListView(ListView):
    model = Word
    template_name = 'recs/random_word_list.html'
    sample_size = 30

    def get_queryset(self):
        language = Language.objects.get(pk=1)
        all_ids = list(Word.objects.filter(
            language=language).values_list('id', flat=True))
        random_ids = random.sample(all_ids, self.sample_size)
        random_objects = Word.objects.filter(id__in=random_ids)
        return random_objects


def get_recommendations(request):
    if request.method == 'POST':
        word_ids = [key for key in request.POST.keys()
                    if key != 'csrfmiddlewaretoken']
        if len(word_ids) == 0:
            return redirect("recsys:test")
        words = Word.objects.filter(pk__in=word_ids)
        if request.user.is_authenticated:
            session = Session(user=request.user)
        else:
            session = Session()
        session.save()
        for w in words:
            cw = ChosenWords(session=session, word=w)
            cw.save()

        recs = get_recommendations_by_word_ids(word_ids)
        recs_set = set()
        for m in recs:
            words_from_model = Word.objects.filter(word__in=recs[m])
            recs_set |= set(recs[m])
            for w in words_from_model:
                cw = RecommendedWords(session=session, word=w, model=m)
                cw.save()

        recs_obj = Word.objects.filter(word__in=recs_set)
        data = {'recs': recs_obj, 'chosen': words, 'session': session}
        return render(request, 'recs/rec_words_list.html', data)
    return redirect("recsys:test")


def save_results(request):
    if request.method == 'POST':
        if 'session' not in request.POST.keys():
            return redirect("recsys:test")
        session_id = request.POST['session']
        session = Session.objects.get(pk=session_id)
        word_ids = [key for key in request.POST.keys()
                    if key not in {'csrfmiddlewaretoken', 'session'}]
        if len(word_ids) == 0:
            return render(request, 'recs/final.html')
        words = Word.objects.filter(pk__in=word_ids)
        for w in words:
            cw = AcceptedRecs(session=session, word=w)
            cw.save()
        return render(request, 'recs/final.html')
    return redirect("recsys:test")
