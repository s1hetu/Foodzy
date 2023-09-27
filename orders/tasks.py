import datetime
import logging

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from FDA.constants import MODE, PURPOSE, NARATION_RESTAURANT, CURRENCY, ACCOUNT_NUMBER, NARATION_AGENT
from delivery_agent.models import AcceptedOrder
from orders.models import Order, OrderPayoutDetail
from orders.services import client
from restaurant.models import Restaurant

logger = logging.getLogger()


@shared_task()
def schedule_payout():
    restaurant_payout.delay()
    agent_payout.delay()



@shared_task()
def restaurant_payout():
    all_restaurants = Restaurant.objects.all()
    for restaurant in all_restaurants:
        today = timezone.now()
        first = today.replace(day=1)
        last_date_of_month = first - datetime.timedelta(days=1)
        first_day_of_month = last_date_of_month.replace(day=1)

        try:
            orders = OrderPayoutDetail.objects.filter(restaurant=restaurant, order__status="delivered",
                                                      order__paid=True, order__cancelled=False,
                                                      order_date__range=[first_day_of_month, last_date_of_month])

            fund_account_id = restaurant.documents.razorpay_fund_account_id

            amount = orders.aggregate(total__sum=Sum('rest_amount'))['total__sum'] * 100

            params = {
                "account_number": ACCOUNT_NUMBER,
                "fund_account_id": str(fund_account_id),
                "amount": int(amount),
                "currency": CURRENCY,
                "mode": MODE,
                "purpose": PURPOSE,
                "narration": NARATION_RESTAURANT,
            }
            restaurant_payouts = client.post(path="/payouts", data=params)
            logger.info(
                f"Amount {amount / 100} transferred to {restaurant} restaurant on fund account {fund_account_id}.....")

            orders.update(razorpay_payout_restaurant_id=restaurant_payouts['id'],
                          payout_date=datetime.datetime.now())
        except Exception as e:
            logger.error(f"Exception occurred for restaurant::{e}")


@shared_task()
def agent_payout():
    if accepted_orders := AcceptedOrder.objects.all().distinct('id', 'agent'):
        for accepted_order in accepted_orders:
            agent = accepted_order.agent
            fund_account_id = agent.document.razorpay_fund_account_id
            today = timezone.now()
            first = today.replace(day=1)
            last_date_of_month = first - datetime.timedelta(days=1)
            first_day_of_month = last_date_of_month.replace(day=1)

            try:
                orders = AcceptedOrder.objects.filter(agent=agent, order__status="delivered", order__cancelled=False,
                                                      order__paid=True, order__order_date__range=[first_day_of_month,
                                                                                                  last_date_of_month]).values_list(
                    'order', flat=True)

                amount = \
                    OrderPayoutDetail.objects.filter(order__id__in=orders).aggregate(total__sum=Sum('agent_amount'))[
                        'total__sum'] * 100

                params = {
                    "account_number": ACCOUNT_NUMBER,
                    "fund_account_id": str(fund_account_id),
                    "amount": int(amount),
                    "currency": CURRENCY,
                    "mode": MODE,
                    "purpose": PURPOSE,
                    "narration": NARATION_AGENT,
                }
                agent_payouts = client.post(path="/payouts", data=params)
                logger.info(f"Amount {amount / 100} transferred to {agent} agent on fund account {fund_account_id}")
                OrderPayoutDetail.objects.filter(order__id__in=orders).update(
                    razorpay_payout_agent_id=agent_payouts['id'],
                    payout_date=datetime.datetime.now())
            except Exception as e:
                logger.error(f"exception occurred for agent::{e}")
    else:
        logger.info("No agents to pay.")


@shared_task()
def reject_order_if_not_accepted(**kwargs):
    order = Order.objects.prefetch_related('items').get(id=kwargs['id'])
    if order.status == 'waiting':
        order.status = 'rejected'
        order.save()

        for item in order.orderitems_set.all():
            item.item.available_quantity += item.quantity
            item.item.save()

        if order.mode == "Online" and order.paid:
            # todo : can be added to celery beat as refund can be scheduled.
            paymentId = order.razorpay_payment_id
            client.payment.refund(paymentId, {
                "amount": int(order.total) * 100,
                "speed": "normal",
                "notes": {
                    "notes_key_1": f"Refund for {order.id} as the order got cancelled.",
                },
            })






