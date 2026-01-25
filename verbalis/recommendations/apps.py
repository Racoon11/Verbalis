from django.apps import AppConfig
import os
import joblib
import json
import torch
from gensim.models import KeyedVectors
from .recmodels import NCFUserEmb, ContentBasedNeuralFilteringModel


class RecommendationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendations'
    knn_user_to_user_model = None
    recsys_base = None
    emb_model = None

    def ready(self):
        self.prepare_models()

        recsys_base_path = os.path.join(os.path.dirname(__file__), 'data',
                                        'data_recsys.json')
        self.recsys_base = json.loads(open(recsys_base_path).read())
        self.user_ids = list(self.recsys_base.keys())

        emb_model_path = os.path.join(os.path.dirname(__file__), 'data',
                                      'GoogleNews-vectors-negative300.bin')
        self.emb_model = KeyedVectors.load_word2vec_format(
            emb_model_path, binary=True)

        return super().ready()

    def get_model_path(self, name):
        model_path = os.path.join(os.path.dirname(__file__), 'models', name)
        return model_path

    def prepare_models(self):
        model_path = self.get_model_path('knn_user_to_user_filtering.pkl')
        self.knn_user_to_user_model = joblib.load(model_path)

        model_path = self.get_model_path('knn_user_to_user_jacquard.pkl')
        self.knn_janquard_model = joblib.load(model_path)

        model_path = self.get_model_path('knn_content_filtering.pkl')
        self.knn_content_filtering = joblib.load(model_path)

        model_path = self.get_model_path('ncf_user_emb.pth')
        self.ncf_user_model = NCFUserEmb(300, 8120)
        self.ncf_user_model.load_state_dict(torch.load(
            model_path, weights_only=True))
        self.ncf_user_model.eval()

        model_path = self.get_model_path('ncf_content.pth')
        self.ncf_content_model = ContentBasedNeuralFilteringModel(300, 64)
        self.ncf_content_model.load_state_dict(torch.load(
            model_path, weights_only=True))
        self.ncf_content_model.eval()
