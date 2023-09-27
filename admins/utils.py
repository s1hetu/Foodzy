import razorpay
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404

from FDA.constants import (
    DEFAULT_PAGINATED_BY, DEFAULT_GET_ELIDED_PAGE_RANGE_ON_EACH_SIDE,
    DEFAULT_GET_ELIDED_PAGE_RANGE_ON_ENDS
)


class CustomPaginator(Paginator):
    def validate_number(self, number):
        try:
            return super().validate_number(number)
        except (EmptyPage, PageNotAnInteger) as e:  # pragma: no cover
            raise Http404 from e


def get_paginated_context(context, request, queryset, paginator_class, paginate_by=None, on_each_side=None,
                          on_ends=None):
    try:
        if not paginate_by:
            paginate_by = int(settings.PAGINATION_CONFIGURATIONS.get(
                'PAGINATE_BY', DEFAULT_PAGINATED_BY)
            )
        if not on_each_side:
            on_each_side = int(settings.PAGINATION_CONFIGURATIONS.get(
                'GET_ELIDED_PAGE_RANGE_ON_EACH_SIDE', DEFAULT_GET_ELIDED_PAGE_RANGE_ON_EACH_SIDE)
            )
        if not on_ends:
            on_ends = int(settings.PAGINATION_CONFIGURATIONS.get(
                'GET_ELIDED_PAGE_RANGE_ON_ENDS', DEFAULT_GET_ELIDED_PAGE_RANGE_ON_ENDS)
            )
    except AttributeError:  # pragma: no cover
        paginate_by = DEFAULT_PAGINATED_BY
        on_each_side = DEFAULT_GET_ELIDED_PAGE_RANGE_ON_EACH_SIDE
        on_ends = DEFAULT_GET_ELIDED_PAGE_RANGE_ON_ENDS

    page = request.GET.get('page', 1)
    paginator = paginator_class(queryset, paginate_by)

    objects = paginator.page(page)
    objects.adjusted_elided_pages = paginator.get_elided_page_range(
        page,
        on_each_side=on_each_side,
        on_ends=on_ends
    )
    context['page_obj'] = objects
    context['current_page_number'] = int(page)

    return context


def create_razorpay_contact(client, name, email, contact, contact_type, reference_id):
    return client.post(path="/contacts/", data={
        "name": name,
        "email": email,
        "contact": contact,
        "type": contact_type,
        "reference_id": reference_id,
    })


def create_fund_account(client, contact_id, user_name, ifsc, account_number):
    return razorpay.FundAccount(client).create(data={
        'contact_id': contact_id,
        'account_type': "bank_account",
        'bank_account': {
            "name": user_name,
            "ifsc": ifsc,
            "account_number": account_number
        }
    })
