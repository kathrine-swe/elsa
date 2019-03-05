# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Investigation


# Create your views here.

@login_required
def context(request):
    context_dict = {
        'investigations':Investigation.objects.all(),
    }

    return render(request, 'context/repository.html', context_dict)

