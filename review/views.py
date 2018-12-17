# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template import Context
from django.template.loader import get_template
from .forms import ReviewForm









# Create your views here.


def index(request):
    review_form = ReviewForm(request.POST or None)
    context_dict = {}
    context_dict['review_form'] = review_form
    context_dict['email_sent'] = False

    
    if review_form.is_valid():
        print 'is valid'

        # Email the profile with the contact information
        template = get_template('review/comment_template.txt')
        context_dict['contact_name'] = '{0}, {1}'.format(request.user.last_name, request.user.first_name)
        context_dict['contact_email'] = request.user.email
        context_dict['agency'] = request.user.userprofile.agency
        context_dict['derived_data'] = review_form.cleaned_data['derived_data']
        context_dict['reviewer'] = review_form.cleaned_data['reviewer']
        context_dict['question1'] = review_form.cleaned_data['question1']
        context_dict['question2'] = review_form.cleaned_data['question2']
        context_dict['question3'] = review_form.cleaned_data['question3']
        context_dict['question4'] = review_form.cleaned_data['question4']
        content = template.render(context_dict)

        email = EmailMessage(
            subject = "Derived Data Peer Review from {}".format(context_dict['contact_name']),
            body = content,
            from_email = context_dict['contact_email'],
            to = ['elsa@atmos.nmsu.edu',],
            headers = {'Reply-To': context_dict['contact_email'] }
        )

        email.send()
        context_dict['email_sent'] = True
        return render(request, 'review/index.html', context_dict)
    return render(request, 'review/index.html', context_dict)
