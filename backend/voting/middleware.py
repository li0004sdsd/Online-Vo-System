from .signals import update_user_activity


class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            update_user_activity(request.user)

        response = self.get_response(request)
        return response
