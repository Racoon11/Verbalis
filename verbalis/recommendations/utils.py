from django.apps import apps
import numpy as np
import torch
from words.models import Word
from languages.models import Language


def sentence_embedding_avg(text, model, til=15):
    word_vectors = [model[word] for word in text[:til] if word in model]
    if not word_vectors:
        return np.zeros(300)
    return np.mean(word_vectors, axis=0)


def user_to_user_filtering(words, knn, conf, is_jaqcuard=False, n_recs=5):
    if not is_jaqcuard:
        emb = sentence_embedding_avg(words, conf.emb_model)
        dists, idxs = knn.kneighbors([emb])
    else:
        words = words[:15]
        words += [0] * (15 - len(words))
        dists, idxs = knn.kneighbors([words])
        words = Word.objects.filter(pk__in=words)
    dists, idxs = dists[0], idxs[0]

    m = np.mean(dists)
    std = np.std(dists)
    words_to_rec = {}
    for i in range(len(idxs)):
        for w in conf.recsys_base[conf.user_ids[idxs[i]]]:
            if w in words:
                continue
            words_to_rec[w] = words_to_rec.get(
                w, 0) + 1 * (1 - (dists[i] - m) / std)
    return sorted(words_to_rec,
                  key=lambda x: words_to_rec[x], reverse=True)[:n_recs]


def content_based_rec(words, knn, conf, n_recs=5):
    recs = {}
    n = len(words)
    cur = 0
    language = Language.objects.get(pk=1)
    words_in_model = [w for w in [w.word for w in 
                                  Word.objects.filter(language=language)]
                      if w in conf.emb_model]
    for w in words:
        if w not in conf.emb_model:
            continue
        dists, idxs = knn.kneighbors([conf.emb_model[w]])
        dists, idxs = dists[0][1:], idxs[0][1:]
        for i in range(15):
            pred_word = words_in_model[idxs[i]]
            recs[pred_word] = recs.get(pred_word, -float('inf'))
            recs[pred_word] = max(recs[pred_word], (n - cur) / n * dists[i])
        cur += 1
    return sorted(recs, key=lambda x: recs[x], reverse=True)[:n_recs]


def recommend_for_words(model, words, word_ids, conf,
                        n_items=8120, top_k=5, exclude_items=True):
    model.eval()
    with torch.no_grad():
        user_vec = torch.tensor([sentence_embedding_avg(
            words, conf.emb_model, -1)]*n_items, dtype=torch.float32)
        item_vec = torch.arange(n_items, dtype=torch.long)
        scores = model(user_vec, item_vec)
        scores = scores.numpy()

        if exclude_items:
            scores[word_ids] = -1  # исключаем уже известные

        top_items = np.argsort(-scores)[:top_k]
        return top_items


def recommend_for_words_content(ncf, words, conf, top_k=5, exclude_items=None):
    ncf.eval()
    with torch.no_grad():
        language = Language.objects.get(pk=1)
        all_words = [w for w in [w.word for w in 
                                 Word.objects.filter(language=language)]
                     if w in conf.emb_model]
        user_vec = torch.tensor([
            sentence_embedding_avg(words, conf.emb_model, -1)]*len(all_words),
            dtype=torch.float32)
        item_vec = torch.tensor([
            conf.emb_model[w] for w in all_words], dtype=torch.float32)
        scores = ncf(user_vec, item_vec)
        scores = scores.cpu().numpy()

        if exclude_items:
            scores[exclude_items] = -1  # исключаем уже известные

        top_items = np.argsort(-scores)[:top_k]
        return [all_words[i] for i in top_items]


def get_recommendations_by_word_ids(word_ids):
    words = Word.objects.filter(pk__in=word_ids)
    words_text = [w.word for w in words]
    words_id = [w.id for w in words]

    conf = apps.get_app_config('recommendations')
    model = conf.knn_user_to_user_model
    recs1 = user_to_user_filtering(words_text, model, conf, False, 5)

    model = conf.knn_janquard_model
    recs2 = user_to_user_filtering(words_id, model, conf, True, 5)

    model = conf.knn_content_filtering
    recs3 = content_based_rec(words_text, model, conf)

    model = conf.ncf_user_model
    rec4 = recommend_for_words(model, words_text, words_id, conf)
    rec4 = [w.word for w in Word.objects.filter(pk__in=rec4)]

    model = conf.ncf_content_model
    rec5 = recommend_for_words_content(model, words_text, conf)

    recs = {'knn_user_to_user_model': recs1,
            'knn_janquard_model': recs2,
            'knn_content_filtering': recs3,
            'ncf_user_model': rec4,
            'ncf_content_model': rec5}
    return recs
