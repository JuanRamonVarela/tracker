from django.urls import path
from . import views

urlpatterns=[
    # dashboard url
    path('', views.index, name='index'),
    # categories url
    path('categories/',  views.CategoriesView, name='categories'),
    path('categories/create/', views.CreateCategory, name='create_category'),
    path('categories/<int:pk>/update/', views.update_category, name='update_category'),
    path('categories/<int:pk>/remove/', views.remove_category, name='remove_category'),
    # books url
    path('books/', views.BooksView, name='books'),
    path('books/create/', views.CreateBook, name='create_books'),
    # login url
    path('login/', views.signin, name='signing'),
]