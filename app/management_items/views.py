from django.core.exceptions import BadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render


def index(request):
    return render(request, "index.html")
