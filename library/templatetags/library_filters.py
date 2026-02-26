from django import template

register = template.Library()

@register.filter
def book_status(value):
    if value:
        return '<span class="text-success">Available</span>'
    return '<span class="text-danger">Fully Borrowed</span>'


@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={'class': css_class})