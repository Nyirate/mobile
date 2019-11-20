from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from mobilapp.forms import RegistrationForm,AccountAuthenticationForm,NewServiceForm
from mobilapp.models import Account,Category,Services

from django.contrib.auth.decorators import login_required
from django.contrib import auth
from .permissions import IsAuthenticatedOrReadOnly


from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import AccountSerializer,CategorySerializer
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
  accounts=Account.objects.all()
  categories=Category.objects.all()
 
  return render(request,'index.html',{"accounts":accounts,"categories":categories})

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

def new_service(request,category_id):
		current_user = request.user
		if request.method == 'POST':
			form = NewServiceForm(request.POST, request.FILES)
			if form.is_valid():
				s_post = form.save(commit=False)
				s_post.user = current_user
				s_post.save()
				return redirect('service',category_id)
		else:
			form = NewServiceForm()
			return render(request,'new_service.html', {"form": form,"category_id":category_id})

def service(request,category_id):
	categories=Category.objects.get(id=category_id)
	services=Services.objects.filter(category=categories.id).all()
	return render(request,'service.html',{"services":services,"category_id":category_id})


