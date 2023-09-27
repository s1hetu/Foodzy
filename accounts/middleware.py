from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from social_core.exceptions import AuthAlreadyAssociated
from social_django.middleware import SocialAuthExceptionMiddleware


class CustomSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):

    def process_exception(self, request, exception):
        if isinstance(exception, AuthAlreadyAssociated):  # pragma: no cover
            messages.error(request, 'This account is already linked with other user. Try using different account.')
            url = self.get_redirect_uri(request, exception)
            return redirect(url)
        return super(CustomSocialAuthExceptionMiddleware, self).process_exception(request, exception)


class BlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if request.user.is_authenticated and request.user.is_blocked:  # pragma: no cover
            messages.error(request, 'Your account is blocked!')
            logout(request)
            return redirect('home')

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
