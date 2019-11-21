from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from mobilapp.forms import *
from mobilapp.models import *

from django.contrib.auth.decorators import login_required
from django.contrib import auth
from .permissions import IsAuthenticatedOrReadOnly


from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import AccountSerializer, CategorySerializer
from rest_framework import status


class AccountList(APIView):
    def get(self, request, format=None):
        all_accounts = Account.objects.all()
        serializers = AccountSerializer(all_accounts, many=True)
        return Response(serializers.data)

    def post(self, request, format=None):
        serializers = AccountSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryList(APIView):
    def get(self, request, format=None):
        all_categories = Category.objects.all()
        serializers = CategorySerializer(all_categories, many=True)
        return Response(serializers.data)

    def post(self, request, format=None):
        serializers = CategorySerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
# @login_required(login_url='/accounts/login/')
def welcome(request):
    # context ={}
    accounts = Account.objects.all()
    categories = Category.objects.all()

    return render(request, 'all_apps/index.html', {"accounts": accounts, "categories": categories})


def logout_view(request):
    logout(request)
    return redirect('/')


def login_view(request):

    context = {}

    # user = request.user
    # if user.is_authenticated:
    # 	return redirect("welcome")

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect("welcome")

    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form

    # print(form)
    return render(request, "registration/login.html", context)


def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            return redirect('welcome')
        else:
            context['registration_form'] = form

    else:
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'registration/registration_form.html', context)


def new_service(request, category_id):
    current_user = request.user
    if request.method == 'POST':
        form = NewServiceForm(request.POST, request.FILES)
        if form.is_valid():
            s_post = form.save(commit=False)
            s_post.user = current_user
            s_post.save()
            return redirect('service', category_id)
    else:
        form = NewServiceForm()
        return render(request, 'all_apps/new_service.html', {"form": form, "category_id": category_id})


def service(request, category_id):
    categories = Category.objects.get(id=category_id)
    services = Services.objects.filter(category=categories.id).all().prefetch_related('comment_set')
    # comment = Comment.objects.filter(service=services).all()
    return render(request, 'all_apps/service.html', {"services": services, "category_id": category_id, "comment": comment})


# @login_required(login_url='/accounts/login/')
def profile_form(request):
    current_user = request.user
    profile = CompanyProfile.objects.filter(user=current_user).first()
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = current_user
            profile.save()
        return redirect('profiledisplay')

    else:
        form = CompanyProfileForm(instance=profile)
    return render(request, 'registration/profile.html', {"form": form})


@login_required(login_url='/accounts/login/')
def company_profile(request):
    current_user = request.user
    business_name = CompanyProfile.objects.all()
    # categories = Category.objects.get(id=category_id)
    comment = Comment.objects.all()
    # email = CompanyProfile.objects.filter(user=current_user)

    # location = CompanyProfile.objects.filter(user=current_user)

    return render(request, 'all_apps/profiledisplay.html', {"business_name": business_name, "current_user": current_user, "comment": comment})


def new_comment(request, service_id):

    current_user = request.user
    service = Services.objects.filter(id=service_id).first()
    companyprofile = CompanyProfile.objects.all()
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = current_user
            comment.service = service
            comment.save()
            return redirect('welcome')

    else:
        form = CommentForm()
    return render(request, 'all_apps/new_comment.html', {"form": form, "service": service, "companyprofile": companyprofile, "service_id": service_id})


def comment(request, service_id):
    try:
        comment = Comment.objects.get(id=service_id).all()
    except DoesNotExist:
        raise Http404()
    return render(request, "all_apps/index.html", {"comment": comment})
