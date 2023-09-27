from django.contrib.auth.models import Permission
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .tasks import send_mail_task


def send_mail(to, template, context):
    html_content = render_to_string(f'accounts/emails/{template}.html', context)
    # send mail using celary
    send_mail_task.delay(context['subject'], html_content, to)


def send_activation_email(request, email, code):
    context = {
        'subject': _('Profile activation'),
        'uri': request.build_absolute_uri(reverse('activate-api', kwargs={'code': code})),
    }
    send_mail(email, 'activate_profile', context)


def send_reset_password_email(request, email, token, uid):
    context = {
        'subject': _('Restore password'),
        'uri': request.build_absolute_uri(
            reverse('restore-password', kwargs={'uidb64': uid, 'token': token})),
    }
    send_mail(email, 'restore_password_email', context)


def add_permissions_to_group(group):
    if group.name == 'delivery_agent':
        perm1 = Permission.objects.get(codename='update_status')
        perm2 = Permission.objects.get(codename='view_acceptedorder')
        perm3 = Permission.objects.get(codename='add_acceptedorder')
        perm4 = Permission.objects.get(codename='change_order')
        perm5 = Permission.objects.get(codename='view_order')
        perm6 = Permission.objects.get(codename='view_activationtime')
        perm7 = Permission.objects.get(codename='view_document')
        group.permissions.add(*[perm1, perm2, perm3, perm4, perm5, perm6, perm7])
    elif group.name == 'restaurant_owner':
        perm1 = Permission.objects.get(codename='view_restaurant')
        perm2 = Permission.objects.get(codename='change_order')
        perm3 = Permission.objects.get(codename='view_order')
        perm4 = Permission.objects.get(codename='view_documents')
        perm5 = Permission.objects.get(codename='add_items')
        perm6 = Permission.objects.get(codename='change_items')
        perm7 = Permission.objects.get(codename='view_items')
        perm8 = Permission.objects.get(codename='view_ratingsandreviews')
        perm9 = Permission.objects.get(codename='add_restaurant')
        perm10 = Permission.objects.get(codename='change_is_accepting_orders_on_restaurant')
        perm11 = Permission.objects.get(codename='add_restaurantgallery')
        perm12 = Permission.objects.get(codename='view_restaurantgallery')
        perm13 = Permission.objects.get(codename='change_restaurantgallery')
        group.permissions.add(
            *[perm1, perm2, perm3, perm4, perm5, perm6, perm7, perm8, perm9, perm10, perm11, perm12, perm13])
    elif group.name == 'customer':
        perm1 = Permission.objects.get(codename='view_restaurant')
        perm2 = Permission.objects.get(codename='change_order')
        perm3 = Permission.objects.get(codename='view_order')
        perm4 = Permission.objects.get(codename='view_items')
        perm5 = Permission.objects.get(codename='add_ratingsandreviews')
        perm6 = Permission.objects.get(codename='add_cart')
        perm7 = Permission.objects.get(codename='view_cart')
        perm8 = Permission.objects.get(codename='change_cartitems')
        perm9 = Permission.objects.get(codename='view_cartitems')
        perm10 = Permission.objects.get(codename='view_acceptedorder')
        perm11 = Permission.objects.get(codename='change_acceptedorder')
        perm12 = Permission.objects.get(codename='add_order')
        perm13 = Permission.objects.get(codename='view_orderitems')
        perm14 = Permission.objects.get(codename='view_ratingsandreviews')
        perm15 = Permission.objects.get(codename='delete_cartitems')
        perm16 = Permission.objects.get(codename='view_restaurantgallery')

        group.permissions.add(
            *[perm1, perm2, perm3, perm4, perm5, perm6, perm7, perm8, perm9, perm10, perm11, perm12, perm13, perm14,
              perm15, perm16])
