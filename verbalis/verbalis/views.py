from django.views.generic import TemplateView


class AboutPage(TemplateView):
    template_name = 'users/about.html'
