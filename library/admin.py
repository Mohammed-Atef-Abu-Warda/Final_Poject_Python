from django.contrib import admin
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.html import format_html

# Register your models here.

from .models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_admin', 'currently_borrowed', 'total_borrowed', 'profile_pic_tag')
    list_filter = ('is_admin',)
    search_fields = ('user__username', 'phone')

    # عرض الصورة مباشرة في صفحة الـ Admin
    def profile_pic_tag(self, obj):
        if obj.profile_pic:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;"/>', obj.profile_pic.url)
        return "-"
    profile_pic_tag.short_description = 'Profile Picture'



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'book_count')
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'available_copies', 'average_rating')
    list_filter = ('category', 'author')
    search_fields = ('title', 'author__name')
    list_per_page = 20

@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrow_date', 'expected_return_date', 'status')
    list_filter = ('status',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating', 'date')
    list_filter = ('rating',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'date')
    search_fields = ('name', 'email')