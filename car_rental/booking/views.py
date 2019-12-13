from django.shortcuts import render


def index(request):
    title = 'Accueil'
    description = ''
    return render(request, 'base.html', {'title': title, 'description': description})




