from django import template

register = template.Library()

@register.filter
def active(users):
    return users.filter(is_active=True)

@register.filter
def staff(users):
    return users.filter(is_staff=True)

@register.filter
def superuser(users):
    return users.filter(is_superuser=True)