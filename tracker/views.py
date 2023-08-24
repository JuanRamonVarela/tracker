from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Categories, Books, Delivery, DeliveryProspect
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

# define categories to use in books forms
categories=Categories.objects.filter(active=True).all().values('id','category').order_by('category')
    
@login_required
def CreateBook(request):
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

@login_required
def update_book(request, pk):
    books=Books.objects.filter(pk=pk, active=True).all().values()
    if request.method=='GET':
        return render(request, 'books/books_update.html',{'books':books,'categories':categories})
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
            
            if Books.objects.filter(pk=pk).update(
                book_code=code,
                title=title,
                subtitle=subtitle,
                author=author,
                publishing_date=released,
                publisher=publisher,
                category_id=category,
                user_id=request.user.id,
                distribution_expense=expense):
                return redirect('books')
        except Exception as err:
            return render(request, "books/books_create.html",{
            'form':request.POST,
            'categories':categories,
            'msg':{'error':err},
            })

@login_required
def remove_book(request, pk):
    if request.method == "POST":
        book=get_object_or_404(Books, pk=pk)
        if request.method=="POST":
            book.delete()
            return redirect('books')
    else:
        return redirect('404')

@login_required
def DeliveryView(request):
    return render(request, 'deliveries/deliveries.html')

@login_required
def CreateDelivery(request):
    if request.method=="GET":
        return render(request, 'deliveries/deliveries_create.html')
    else:
        try:
            # get category from POST
            book=request.POST['book_code']
            qty=request.POST["qty"]
            date=request.POST['date']
            # validate category value
            if book.isspace()==True:
                raise Exception("The book code can't be just spaces")
            # Search book
            # print(book)
            book_row=Books.objects.filter(book_code=book).all().values()
            # if doesn't exist trhow except
            if len(book_row) == 0:
                raise Exception("Book not found. Try with another book code.")
            # if exist get info
            #print(book_row)
            book_code=book_row[0]['id']
            category=book_row[0]['category_id']
            price=book_row[0]['distribution_expense']
            total=int(qty)*float(price)
            #print(price)
            #format 2 decimals
            total=float(f'{total:.2f}')
            #print(total)
            
            delit=Delivery.objects.create(
                book_id=book_code,
                category_id=category,
                unit_price=price,
                qty=qty,
                total=total,
                date=date,
                user_id=request.user.id
            )
            # if insert redirect to categories
            if delit:
                return redirect('deliveries')
        except Exception as err:
            return render(request, "deliveries/deliveries_create.html",{
                'form':request.POST, 
                'msg':{'error':err},
            })

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