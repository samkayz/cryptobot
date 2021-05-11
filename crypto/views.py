from django.http import request
from django.http import response
from django.shortcuts import render, redirect
import requests
from django.contrib import messages
import json
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from crypto.settings import EMAIL_FROM
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from django.core.paginator import Paginator
import random
import string
import uuid
import datetime
import secrets
from django.db.models import Q
from datetime import datetime
from django.contrib.auth import get_user_model, authenticate, login as dj_login, logout as s_logout
from django.contrib.auth import user_logged_in
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
User = get_user_model()
from django.dispatch.dispatcher import receiver
from user.models import *
import io
import csv
import time
from django.utils import timezone
from datetime import timedelta
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template





@receiver(user_logged_in)
def remove_other_sessions(sender, user, request, **kwargs):
    # remove other sessions
    Session.objects.filter(usersession__user=user).delete()

    # save current session
    request.session.save()

    # create a link from the user to the current session (for later removal)
    UserSession.objects.get_or_create(
        user=user,
        session=Session.objects.get(pk=request.session.session_key)
    )
    
    
def index(request):
    return render(request, 'index.html')


def login(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')
    elif request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        u = get_object_or_404(User, email=email)
        if u.is_active == False:
            messages.info(request, "Your Account has not been Verified or Account Deactivated")
            return redirect('/login')
        else:
            user = authenticate(email=email, password=password)
            if user is not None:
            
                dj_login(request, user)
                request.session.set_expiry(600)
                messages.success(request, f'Welcome to Tradify {u.fullname}')
                return redirect('/dashboard')
            else:
                messages.error(request, "Invalid Details")
                return redirect('/login')
    else:
        return render(request, 'login.html')


def signup(request):
    N = 100
    tokens = ''.join(secrets.choice(string.ascii_lowercase + string.digits)for i in range(N))
    url = request.get_host()
    if request.user.is_authenticated:
        return redirect('/dashboard')
    elif request.method == "POST":
        fullname = request.POST['fullname']
        email = request.POST['email']
        mobile = request.POST['mobile']
        country = request.POST['country']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if country == "":
            messages.error(request, "Please select your country of residence")
            return render(request, 'signup.html', {'fullname':fullname, 'email':email, 'mobile':mobile})
        
        elif User.objects.filter(email=email).exists() or User.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile Number/Email Used")
            return render(request, 'signup.html', {'fullname':fullname, 'email':email, 'mobile':mobile})
        
        elif password1 == password2:
            user = User.objects.create_user(fullname=fullname, email=email, mobile=mobile, password=password1, country=country, is_user=True, is_active=False)
            user.save()
            tken = VerifyToken(email=email, tokens=tokens, user=user)
            tken.save()
            verify_link = f'http://{url}/verify?email={email}&token={tokens}'
            
            ### Sending Verification Email #####
            subject, from_email, to = 'Tradify Verification', EMAIL_FROM, email
            html_content = render_to_string('email/verify.html', {'verify_link': verify_link, 'fullname': fullname})
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            messages.success(request, "Registration Successful. Check your Email for verification Link")
            return redirect('/signup')
        else:
            messages.error(request, "Password Missmatch")
            return render(request, 'signup.html', {'fullname':fullname, 'email':email, 'mobile':mobile})
    else:
        return render(request, 'signup.html')
    

def verify(request):
    email = request.GET['email']
    token = request.GET['token']
    if VerifyToken.objects.filter(email=email, tokens=token).exists():
        v = get_object_or_404(VerifyToken, email=email, tokens=token)
        us = get_object_or_404(User, email=email)
        if v.is_used == True:
            messages.warning(request, "Your Account has been verified, Kindly proceed and Login to your account")
            return redirect('/login')
        else:
            u = VerifyToken.objects.filter(email=email, tokens=token)
            u.update(is_used=True)
            usp = User.objects.filter(email=v.email)
            usp.update(is_active=True)
            
            url = request.get_host()
            
            ### Sending Verification Email #####
            subject, from_email, to = 'Tradify Verification', EMAIL_FROM, email
            html_content = render_to_string('email/verify_done.html', {'url':url ,'fullname': us.fullname})
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            messages.success(request, "Account Verified. Kindly proceed and Login to your account")
            return redirect('/login')
    else:
        messages.error(request, "Verification Error. kindly click on resend verification link")
        return redirect('/login')