from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import *
from .forms import *  # You'll define forms below

from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, get_object_or_404

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from library.models import Borrow

from .models import Book, Category, Author, Profile, Review

from .forms import ReviewForm




def all_books(request):
    books = Book.objects.all()
    return render(request, 'library/all_books.html', {
        'books': books
    })





def categories(request):
    categories = Category.objects.all()
    return render(request, 'library/categories.html', {
        'categories': categories
    })


def authors(request):
    authors = Author.objects.all()
    return render(request, 'library/authors.html', {
        'authors': authors
    })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # هنا يمكنك معالجة البيانات (مثل إرسال إيميل)
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message_text = form.cleaned_data['message']
            
            form.save()  # ✅ هذا يحفظ البيانات في قاعدة البيانات
            messages.success(request, "Thank you for contacting us! We will respond soon.")
            return redirect('contact')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()
    
    return render(request, 'library/contact.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    # فحص إذا كان المستخدم مسجل الدخول مسبقاً لإعادة توجيهه للمكان الصحيح
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin:index')
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {user.username}!')
                
                # التحقق هل المستخدم أدمن أم طالب
                if user.is_superuser or user.is_staff:
                    return redirect('admin:index')  # تحويل الأدمن لصفحة إدارة دجانغو
                else:
                    return redirect('home')         # تحويل الطالب للصفحة الرئيسية
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'library/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # تعيين كلمة المرور بشكل مشفر
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'library/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

@login_required
def profile(request):
    user = request.user
    currently_borrowed_count = Borrow.objects.filter(user=user, status='borrowed').count()
    total_borrowed_count = Borrow.objects.filter(user=user).count()
    
    context = {
        'currently_borrowed_count': currently_borrowed_count,
        'total_borrowed_count': total_borrowed_count,
    }
    
    return render(request, 'library/profile.html', context)

@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if  profile_form.is_valid():
            profile_form.save()
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=profile)

    return render(request, 'library/edit_profile.html', {
        'profile_form': profile_form
    })


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if book.available_copies <= 0:
        messages.error(request, "This book is currently not available.")
        return redirect('book_details', id=book.id)

    # تحقق إذا كان المستخدم مستعير الكتاب مسبقًا
    if Borrow.objects.filter(
        book=book,
        user=request.user,
        status='borrowed'
    ).exists():
        messages.error(request, "You have already borrowed this book.")
        return redirect('book_details', id=book.id)

    Borrow.objects.create(
        book=book,
        user=request.user,
        status='borrowed',
        expected_return_date=timezone.now().date() + timedelta(days=7)
    )

    book.available_copies -= 1
    book.save()

    messages.success(request, "You have successfully borrowed the book!")
    return redirect('book_details', id=book.id)

@login_required
def return_book(request, borrow_id):
    borrow = get_object_or_404(
        Borrow,
        id=borrow_id,
        user=request.user,
        status='borrowed'
    )

    borrow.status = 'returned'
    borrow.return_date = timezone.now().date()
    borrow.save()

    borrow.book.available_copies += 1
    borrow.book.save()

    messages.success(request, "You have successfully returned the book!")
    return redirect('my_books')

@login_required
def my_books(request):
    borrowed_books = Borrow.objects.filter(
        user=request.user,
        status='borrowed'
    ).select_related('book')

    return render(request, 'library/my_books.html', {
        'borrowed_books': borrowed_books
    })





def book_details(request, id):
    book = get_object_or_404(Book, pk=id)
    reviews = book.review_set.select_related('user__profile').all()
    average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']

    # تحقق إذا كان المستخدم قد استعار الكتاب
    user_borrowed = False
    borrow_instance = None
    user_reviewed = False
    user = request.user

    if request.user.is_authenticated:
        user_reviewed = Review.objects.filter(
            book=book,
            user=request.user
        ).exists()

        user_borrowed = Borrow.objects.filter(
            book=book,
            user=request.user,
            status='borrowed'
        ).exists()

    if request.user.is_authenticated:
        # البحث عن سجل استعارة هذا الكتاب من قبل المستخدم
        borrow_instance = Borrow.objects.filter(book=book, user=request.user, status=False).first()
        if borrow_instance:
            user_borrowed = True

    return render(request, 'library/book_details.html', {
        'book': book,
        'reviews': reviews,
        'average_rating': average_rating,
        'user_borrowed': user_borrowed,
        'borrow_instance': borrow_instance,  # تم تمرير الكائن للإرجاع لاحقًا
        'user' : user,
    })


@login_required
def add_review(request, id):
    book = get_object_or_404(Book, pk=id)
    user = request.user

    # تحقق من أن المستخدم مسجل
    if not user.is_authenticated:
        messages.error(request, "You need to log in to add a review.")
        return redirect('login')

    # تحقق من عدم وجود مراجعة مسبقة
    if Review.objects.filter(book=book, user=user).exists():
        messages.error(request, "You have already reviewed this book.")
        return redirect('book_details', id=book.id)

    # تحقق إذا المستخدم استعار الكتاب سابقًا
    profile = get_object_or_404(Profile, user=user)
    # تحقق إذا المستخدم استعار هذا الكتاب تحديدًا
    if not Borrow.objects.filter(user=user, book=book).exists():
        messages.error(request, "You need to borrow this book before adding a review.")
        return redirect('book_details', id=book.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = user
            review.save()
            messages.success(request, "Your review has been added successfully!")
            return redirect('book_details', id=book.id)
    else:
        form = ReviewForm()

    return render(request, 'library/add_review.html', {'form': form, 'book': book})



def category_books(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    books = Book.objects.filter(category=category)
    return render(request, 'library/category_books.html', {'category': category, 'books': books})

def author_books(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    books = author.book_set.all()
    return render(request, 'library/author_books.html', {'author': author, 'books': books})

def home(request):
    recent_books = Book.objects.order_by('-id')[:6]
    top_rated = Book.objects.annotate(avg_rating=models.Avg('review__rating')).order_by('-avg_rating')[:3]
    stats = {
        'books': Book.objects.count(),
        'authors': Author.objects.count(),
        'students': User.objects.filter(profile__is_admin=False).count(),
    }
    return render(request, 'library/home.html', {'recent_books': recent_books, 'top_rated': top_rated, 'stats': stats})

# def all_books(request):
#     books = Book.objects.all()
#     # Search, filter, sort logic here (similar to below)
#     paginator = Paginator(books, 9)
#     page = request.GET.get('page')
#     books = paginator.get_page(page)
#     return render(request, 'all_books.html', {'books': books})

# def book_details(request, id):
#     book = get_object_or_404(Book, id=id)
#     reviews = Review.objects.filter(book=book)
#     can_borrow = request.user.is_authenticated and book.is_available and not Borrow.objects.filter(user=request.user, book=book, status='borrowed').exists()
#     return render(request, 'book_details.html', {'book': book, 'reviews': reviews, 'can_borrow': can_borrow})

# @login_required
# def borrow_book(request, book_id):
#     book = get_object_or_404(Book, id=book_id)
#     if book.available_copies > 0 and not Borrow.objects.filter(user=request.user, book=book, status='borrowed').exists():
#         Borrow.objects.create(user=request.user, book=book, expected_return_date=timezone.now() + timedelta(days=14))
#         book.available_copies -= 1
#         book.save()
#         messages.success(request, 'Book borrowed successfully!')
#     return redirect('book_details', id=book_id)

# # Add similar views for other pages (e.g., categories, authors, contact, login, register, etc.)
# # For login/register, use Django's auth views or custom as below.

# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)
#             return redirect('home')
#         messages.error(request, 'Invalid credentials')
#     return render(request, 'login.html')

# def register(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('home')
#     else:
#         form = RegisterForm()
#     return render(request, 'register.html', {'form': form})


# def categories(request):
#     categories = Category.objects.all()
#     return render(request, 'library/categories.html', {
#         'categories': categories
#     })    


# def authors(request):
#     authors = Author.objects.all()
#     return render(request, 'library/authors.html', {
#         'authors': authors
#     })
