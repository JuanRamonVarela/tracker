from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Categories, Books
# Create your views here.

@login_required
def index(request):
    return render(request, 'index.html',{'user':request.user})

def validateCategory(category):
    if category.isspace()==True:
                raise Exception("The category can't be just spaces")
            
    elif category.isnumeric():
        raise Exception("The category can't be just numbers")
    
    else:
        valid_symbols = " .!()+=&-"
        for ch in category:
            if ch not in valid_symbols:
                just_symbols=False
            else:
                just_symbols=True

    if just_symbols:
        raise Exception("Your input contains symbols only")
    
def CategoriesView(request):
    categories=Categories.objects.filter(active=True).all()
    return render(request, 'categories/categories.html',{'data':categories})

@login_required
def CreateCategory(request):
    if request.method=="GET":
        return render(request, 'categories/categories_create.html')
    else:
        try:
            # get category from POST
            category=request.POST['category']
            # validate category value
            validateCategory(category)
            cat=Categories.objects.create(
                category=request.POST['category'],
                user_id=request.user.id
            )
            if cat:
                return redirect('categories')
        except Exception as err:
            return render(request, "categories/categories_create.html",{
                'form':request.POST, 
                'msg':{'error':err},
            })

@login_required
def update_category(request, pk):
    if request.method=="GET":
        cat=get_object_or_404(Categories, pk=pk)
        return render(request, 'categories/categories_update.html', {'data':cat})
    else:
        try:
            cat=request.POST['category']
            validateCategory(cat)
            if Categories.objects.filter(pk=pk).update(category=cat):
                return redirect('categories')
        except Exception as err:
            return render(request, "categories/categories_update.html",{
                'form':request.POST, 
                'msg':{'error':err},
            })

@login_required
def remove_category(request, pk):
    cat=get_object_or_404(Categories, pk=pk)
    if request.method=="POST":
        cat.delete()
        return redirect('categories')

@login_required
def BooksView(request):
    if request.method=="GET":
        return render(request, 'books/books.html',{})
    
def signin(request):
    if request.method=="GET":
        return render(request, 'signin.html',{
            'form':AuthenticationForm
        })
    else:
        user=authenticate(request, username=request.POST['username'],
                     password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html',{
            'form':AuthenticationForm,
            'error':'Usuario o contrasena incorrecto'
            })
        else:
            login(request, user)
            return redirect('index')