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

def validate(field, value):
    # validate no only spaces
    if value.isspace()==True:
                raise Exception("The "+field+" can't be just spaces")
    
    # validate no only numbers
    elif value.isnumeric():
        raise Exception("The "+field+" can't be just numbers")
    
    # validate no only symbols
    else:
        valid_symbols = " .!()+=&-"
        for ch in value:
            if ch not in valid_symbols:
                just_symbols=False
            else:
                just_symbols=True

    if just_symbols:
        raise Exception("The "+field+" can't be just symbols")
    
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
            validate('caregory',category)
            cat=Categories.objects.create(
                category=request.POST['category'],
                user_id=request.user.id
            )
            # if insert redirect to categories
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
            validate('category', cat)
            if Categories.objects.filter(pk=pk).update(category=cat):
                return redirect('categories')
        except Exception as err:
            return render(request, "categories/categories_update.html",{
                'form':request.POST, 
                'msg':{'error':err},
            })

@login_required
def remove_category(request, pk):
    if request.method=="POST":
        cat=get_object_or_404(Categories, pk=pk)
        cat.delete()
        return redirect('categories')
    else:
        return redirect('404')

@login_required
def BooksView(request):
    if request.method=="GET":
        books=Books.objects.filter(active=True).all()
        return render(request, 'books/books.html',{'books':books})

@login_required
def CreateBook(request):
    categories=Categories.objects.filter(active=True).all().values('id','category').order_by('category')
    if request.method=="GET":
        return render(request, 'books/books_create.html',{'categories':categories})
    else:
        try:
            # get data from POST
            code=request.POST['code']
            title=request.POST['title']
            subtitle=request.POST["subtitle"]
            author=request.POST['author']
            released=request.POST["released"]
            publisher=request.POST["publisher"]
            category=request.POST["category"]
            expense=request.POST["expense"]
            
            # validate fields value
            validate('book', title)
            validate('subtitle', subtitle)
            validate('author', author)
            validate('publisher', publisher)

            book=Books.objects.create(
                book_code=code,
                title=title,
                subtitle=subtitle,
                author=author,
                publishing_date=released,
                publisher=publisher,
                category_id=category,
                user_id=request.user.id,
                distribution_expense=expense
            )
            if book:
                return redirect('books')
        except Exception as err:
            return render(request, "books/books_create.html",{
                'form':request.POST,
                'categories':categories,
                'msg':{'error':err},
            })
        
def remove_book(request, pk):
    if request.method == "POST":
        book=get_object_or_404(Books, pk=pk)
        if request.method=="POST":
            book.delete()
            return redirect('books')
    else:
        return redirect('404')

def not_found(request):
    return render(request, '404.html')

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