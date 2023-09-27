from django.core.exceptions import PermissionDenied


class GroupRequiredMixin(object):
    """
        group_required - list of strings, required param
    """

    group_required = None

    def dispatch(self, request, *args, **kwargs):
        user_groups = list(request.user.groups.values_list('name', flat=True))
        if self.group_required and (not (set(user_groups).intersection(self.group_required)) or (
                user_groups[0] == 'delivery_agent' and not request.user.document.is_verified) or
                                    (user_groups[
                                         0] == 'restaurant' and not request.user.restaurants.documents.is_verified)):
            raise PermissionDenied

        return super(GroupRequiredMixin, self).dispatch(request, *args, **kwargs)
