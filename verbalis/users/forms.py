# users/forms.py
import io
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image

# Получаем модель пользователя:
User = get_user_model()


class CustomUserCreationForm(UserCreationForm):

    # Наследуем класс Meta от соответствующего класса родительской формы.
    # Так этот класс будет не перезаписан, а расширен.
    class Meta(UserCreationForm.Meta):
        model = User
        # fields = ('username',)


class CustomUserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('cur_language', 'image',)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image or not hasattr(image, 'read'):
            return image
        img = Image.open(image)
        if img.width != img.height:
            size = min(img.width, img.height)
            left = (img.width - size) // 2
            top = (img.height - size) // 2
            img = img.crop((left, top, left + size, top + size))
        img = img.resize((400, 400), Image.LANCZOS)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)
        return InMemoryUploadedFile(
            buf, 'image', image.name, 'image/jpeg', buf.getbuffer().nbytes, None
        )
