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
    path('books/<int:pk>/update/', views.update_book, name='update_book'),
    path('books/<int:pk>/remove/', views.remove_book, name='remove_book'),
    
    # delivery url
    path('delivery/', views.DeliveryView, name='deliveries'),
    path('delivery/create/', views.CreateDelivery, name='create_deliveries'),
    path('delivery/<int:pk>/update/', views.update_deliveries, name='update_deliveries'),
    path('delivery/<int:pk>/remove/', views.remove_deliveries, name='remove_deliveries'),
    
    # login url
    path('login/', views.signin, name='signing'),
    path('404/', views.not_found, name='404' ),
]