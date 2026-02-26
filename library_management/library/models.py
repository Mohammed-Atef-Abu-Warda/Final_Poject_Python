from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True)
    is_admin = models.BooleanField(default=False)  # For admin distinction
    
    currently_borrowed = models.PositiveIntegerField(default=0)
    total_borrowed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username




class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # e.g., FontAwesome icon class

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='authors/', blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def book_count(self):
        return self.book_set.count()

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    cover_image = models.ImageField(upload_to='books/')
    pub_year = models.IntegerField()
    pages = models.IntegerField()
    language = models.CharField(max_length=50)
    description = models.TextField()
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.available_copies > 0

    @property
    def average_rating(self):
        reviews = self.review_set.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0

class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField()  # حقل NOT NULL

    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('borrowed', 'Borrowed'), ('returned', 'Returned')], default='borrowed')

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')  # One review per user per book

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject