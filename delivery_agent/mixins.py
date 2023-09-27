from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from delivery_agent.models import AcceptedOrder, AdditionalDetail
from orders.models import Order


class CheckOrderAgentMixin:
    def dispatch(self, request, *args, **kwargs):
        order_obj = Order.get_object_from_pk(pk=kwargs['pk'])
        if hasattr(order_obj, 'accepted_order'):
            if AcceptedOrder.get_agent_from_order_id(kwargs['pk']) == request.user:
                return super(CheckOrderAgentMixin, self).dispatch(request, *args, **kwargs)
            else:
                raise PermissionDenied
        elif (order_obj.status not in ['waiting',
                                       'rejected']) and order_obj.restaurant.address.city.id == request.user.addresses.values().first().get(
                'city_id'):
            return super(CheckOrderAgentMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied


class VerifiedAgentRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        agent = request.user
        if not hasattr(agent, 'document'):
            raise PermissionDenied
        elif not agent.document.is_verified or agent.document.application_status != 'approved':
            return redirect('agent-application-status')
        return super(VerifiedAgentRequiredMixin, self).dispatch(request, *args, **kwargs)


class AvailableAgentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        status = AdditionalDetail.get_agent_status(request.user)
        if not status or status == 'Not Available':
            return redirect('not-available')

        return super(AvailableAgentRequiredMixin, self).dispatch(request, *args, **kwargs)


class LatLongRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.GET.get('lat') or not request.GET.get('long'):
            return render(request, 'delivery_agent/get_coordinates.html', {'redirect_to': 'see-available-deliveries'})
        return super().dispatch(request, *args, **kwargs)
