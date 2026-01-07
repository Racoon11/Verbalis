from django import forms
from .models import Collection, Word


class CollectionCreationForm(forms.ModelForm):

    words = forms.ModelMultipleChoiceField(
        queryset=Word.objects.none(),  # будет переопределено в __init__
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
    )

    class Meta:
        model = Collection
        fields = ('name', 'description', 'is_public', 'words')

    def __init__(self, *args, **kwargs):
        # Передаём язык через инициализацию формы
        language = kwargs.pop('language', None)
        super().__init__(*args, **kwargs)

        if language:
            self.fields['words'].queryset = Word.objects.filter(
                language=language)
        else:
            self.fields['words'].queryset = Word.objects.all()


class AddWordToCollectionForm(forms.Form):
    collection_id = forms.ModelChoiceField(
        queryset=Collection.objects.none(),
        label="Коллекция"
    )
    word_id = forms.IntegerField()

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['collection_id'].queryset = Collection.objects.filter(
            owner=user)
