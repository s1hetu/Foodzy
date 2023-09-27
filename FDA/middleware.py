from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render
from rest_framework import status


class ExceptionHandleMiddleware:
    """
    Custom Middleware to render Page
    """

    def __init__(self, get_response):
        """
        One-time configuration and initialisation.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Code to be executed for each request before the view (and later
        middleware) are called.
        """

        response = self.get_response(request)
        if response.status_code == 404:
            return render(
                request=request,
                template_name='delivery_agent/404_not_found.html',
                status=404
            )
        if response.status_code == 204:
            return render(request, 'delivery_agent/not_found.html', status=status.HTTP_204_NO_CONTENT)

        return response

    def process_exception(self, request, exception):
        # This is the method that responsible for the safe-exception handling
        if isinstance(exception, PermissionDenied):
            return render(
                request=request,
                template_name='delivery_agent/403_forbidden.html',
                status=403
            )
        if isinstance(exception, Http404):
            return render(
                request=request,
                template_name='delivery_agent/404_not_found.html',
                status=404
            )
        return None
