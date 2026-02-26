from django.urls import path
from . import views


# app_name = 'library'


urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.all_books, name='all_books'),
    path('book/<int:id>/', views.book_details, name='book_details'),
    path('categories/', views.categories, name='categories'),
    path('categories/<int:category_id>/books/', views.category_books, name='category_books'),
    path('authors/', views.authors, name='authors'),
    path('authors/<int:author_id>/books/', views.author_books, name='author_books'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('borrow/<int:borrow_id>/return/', views.return_book, name='return_book'),
    path('my-books/', views.my_books, name='my_books'),
    path('book/<int:id>/review/', views.add_review, name='add_review'),
    path('logout/', views.logout_view, name='logout'),
    path('books/<int:id>/add_review/', views.add_review, name='add_review'),

]