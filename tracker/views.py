from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Categories, Books, Delivery
from datetime import date, timedelta
from django.db.models import Sum, DecimalField, IntegerField, OuterRef, Subquery
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.http import Http404
import random
# Create your views here.

# insert aleatory using random and time delta
# start_date = date(2023, 8, 26)
# end_date = date(2023, 12, 31)
# delta = timedelta(days=1)
# while start_date <= end_date:
#     print(start_date.strftime("%Y-%m-%d"))
#     for i in range(30):
#         book=random.randint(1,11)
#         book_data=Books.objects.filter(pk=book).all()
#         category=book_data[0].category_id
#         price=book_data[0].distribution_expense
#         qty=random.randint(1,5)
#         total=int(qty)*float(price)
#         total=float(f'{total:.2f}')
#         fecha=start_date.strftime("%Y-%m-%d")
#         print(fecha)

#         delit=Delivery.objects.create(
#             book_id=book,
#             category_id=category,
#             unit_price=price,
#             qty=qty,
#             total=total,
#             date=fecha,
#             user_id=1
#         )
#     start_date += delta


# Test data, make data filter and pagination

@login_required
def index(request):
    today = date.today().strftime("%Y-%m-%d")
    month=date.today().strftime("%m")
    # calculate today deliveries
    #deliveries_today=Delivery.objects.raw("SELECT id, sum(total) as total, sum(qty) as qty  from tracker_delivery WHERE date='"+d1+"'")
    deliveries_today=Delivery.objects.filter(date=today).aggregate(Sum('qty'), Sum('total'))
    # calculate month deliveries
    deliveries_month=Delivery.objects.filter(date__month=month).aggregate(Sum('qty'), Sum('total'))
    # calculate today categories expense

    # prepare a subquery to get categories name
    cat_subquery=Categories.objects.filter(id=OuterRef('category_id')).values('category')
     # get total and cateries name by today
    chart_today=Delivery.objects.filter(date=today).values('category').annotate(
    total=Sum(('total'), output_field=DecimalField()),
    category_name=Subquery(cat_subquery))
    # get total and cateries name by month
    chart_month=Delivery.objects.filter(date__month=month).values('category').annotate(
    total=Sum(('total'), output_field=DecimalField()),
    category_name=Subquery(cat_subquery))
    
    #Report month categories line

    # top books today
    book_subquery=Books.objects.filter(id=OuterRef('book_id')).values('title')
    book_code_subquery=Books.objects.filter(id=OuterRef('book_id')).values('book_code')
    
    # handling error when records lower than limit
    def getTopToday(limit):
        try:
            top_today=Delivery.objects.filter(date=today).values('book_id').annotate(
            total=Sum('total', output_field=DecimalField()), qty=Sum('qty', output_field=IntegerField()), 
            title= Subquery(book_subquery), code= Subquery(book_code_subquery)).order_by('-qty')[:limit]
            return top_today
        except IndexError:
            if limit==0:
                top_today={'no-info':"No information to show"}
                return top_today
    
            return None
    
    limit=5
    top_today=getTopToday(limit)
    while(top_today==None):
        limit=limit-1
        top_today=getTopToday(limit)

    #funtion to get top 5 at the month
    def getTopMonth(limit):
        try:
            top_month=Delivery.objects.filter(date__month=month).values('book_id').annotate(
            total=Sum('total', output_field=DecimalField()), qty=Sum('qty', output_field=IntegerField()), 
            title= Subquery(book_subquery), code= Subquery(book_code_subquery)).order_by('-qty')[:limit]
            return top_month
        except IndexError:
            # if limit records 0 no results yet 
            if limit==0:
                top_month={'no-info':"No information to show"}
                return top_month
            # if out of range
            return None
    # limit records
    limit2=5
    top_month=getTopMonth(limit2)
    while(top_month==None):
        limit2=limit2-1
        top_month=getTopMonth(limit2)

    #get lasts deliveries
    limit3=5
    last_deliveries=Delivery.objects.all().order_by('-date','-id')[:limit3]
    # print(last_deliveries)

    area_chart=Delivery.objects.filter(date__month=month).values('date').annotate(
    total=Sum(('total'), output_field=DecimalField()),
    category_name=Subquery(cat_subquery))

    return render(request, 'index.html',{'user':request.user, 'data':{'dev_today':deliveries_today,
    'dev_month':deliveries_month}, 'chart_today':chart_today, 'chart_month':chart_month,
    'top_today':top_today, 'top_month':top_month, "last":last_deliveries, 'area_chart':area_chart})

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
        
        if field=="subtitle":
            just_symbols=False

        if just_symbols:
            raise Exception("The "+field+" can't be just symbols")


@login_required
def DeliveryView(request):
    if request.method=="GET":
        today = date.today().strftime("%Y-%m-%d")
        page=request.GET.get('page',1)
        deliveries=Delivery.objects.filter(active=True, date=today).all().order_by('-date','-id')
        try:
            paginator=Paginator(deliveries,5)
            deliveries=paginator.page(page)
        except:
            raise Http404
        return render(request, 'deliveries/deliveries.html', {'entity':deliveries, 'paginator':paginator})
        
    else:
        # print(request.POST)
        deliveries=Delivery.objects.filter(active=True).all().order_by('-date','-id')
        return render(request, 'deliveries/deliveries.html', {'data':request.POST,'deliveries':deliveries})
    
def DeliveryOptions(request, t, pk):
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
    book_code=book_row[0]['id']
    category=book_row[0]['category_id']
    price=book_row[0]['distribution_expense']
    total=int(qty)*float(price)

    #format 2 decimals
    total=float(f'{total:.2f}')
    #print(total)
    if t=="add":
        delit=Delivery.objects.create(
            book_id=book_code,
            category_id=category,
            unit_price=price,
            qty=qty,
            total=total,
            date=date,
            user_id=request.user.id
        )
        if delit:
            return True
    else:
        if Delivery.objects.filter(pk=pk).update(
                book_id=book_code,
                category_id=category,
                unit_price=price,
                qty=qty,
                total=total,
                date=date,
                user_id=request.user.id
            ):
            # if update redirect to deliveries
            return True

@login_required
def CreateDelivery(request):
    if request.method=="GET":
        return render(request, 'deliveries/deliveries_create.html')
    else:
        try:
            if DeliveryOptions(request, 'add', ''):
                # if insert redirect to deliveries
                return redirect('deliveries')
            else:
                raise Exception("Unkwon Error. Contact us.")
        except Exception as err:
            return render(request, "deliveries/deliveries_create.html",{
                'form':request.POST, 
                'msg':{'error':err},
            })

@login_required
def update_deliveries(request, pk):
    if request.method=="GET":
        deliveries=Delivery.objects.filter(pk=pk).all()
        if len(deliveries)==0:
            return redirect('404')
        return render(request, 'deliveries/deliveries_update.html', {'deliveries':deliveries[0]})
    else:
        try:
            if DeliveryOptions(request, 'upt', pk):
                # if insert redirect to deliveries
                return redirect('deliveries')
        except Exception as err:
            return render(request, "deliveries/deliveries_update.html",{
                'form':request.POST, 
                'msg':{'error':err},
            })

@login_required
def remove_deliveries(request, pk):
    if request.method == "POST":
        delivery=get_object_or_404(Delivery, pk=pk)
        if request.method=="POST":
            delivery.delete()
            return redirect('deliveries')
    else:
        return redirect('404')

@login_required
def CategoriesView(request):
    if request.method=="GET":
        page=request.GET.get('page',1)
        categories=Categories.objects.filter(active=True).all().order_by('category')
        try:
            paginator=Paginator(categories,2)
            categories=paginator.page(page)
        except:
            raise Http404
        
        return render(request, 'categories/categories.html',{'entity':categories, 'paginator':paginator})
    else:
        redirect('categories')

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
        page=request.GET.get('page',1)
        books=Books.objects.filter(active=True).all().order_by('-publishing_date', '-id')
        try:
            paginator=Paginator(books,2)
            books=paginator.page(page)
        except:
            raise Http404
        
        return render(request, 'books/books.html',{'entity':books, 'paginator':paginator})

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

def ReportView(request):
    if request.method=="GET":
        page=request.GET.get('page',1)
        deliveries=Delivery.objects.filter(active=True).all().order_by('-date','-id')
        try:
            paginator=Paginator(deliveries,5)
            deliveries=paginator.page(page)
        except:
            raise Http404
        
        return render(request, 'reports/reports.html', {'entity':deliveries, 'paginator':paginator})

def not_found(request):
    return render(request, '404.html')

def signup(request):
    ### if method is Get
    if request.method=="GET":
        return render(request, 'signup.html')
    else:
        if request.POST['password1']==request.POST["password2"]:
            try:
                user=User.objects.create_user(username=request.POST["username"], 
                                              password=request.POST["password1"])
                user.save()
                login(request, user)
                return redirect("index")
            except InterruptedError:
                return render(request, 'signup.html',{
                            'form':{'username':request.POST['username']},
                            'error':"Usario Registrado"
                        })
            except IntegrityError:
                return render(request, 'signup.html',{
                            'form':{'username':request.POST['username']},
                            'error':"Usario Registrado"
                        })
            
        return render(request, 'signup.html',{
            'form':{'username':request.POST['username']},
            'error':"Passwords no match"
        })

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
            'error':'User or password wrong. Please try again'
            })
        else:
            login(request, user)
            return redirect('index')

@login_required
def signout(request):
    logout(request)
    return redirect('signin')
