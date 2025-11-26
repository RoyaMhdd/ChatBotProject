from users.models import User

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.session.get("auth_token")

        if token:
            try:
                request.user = User.objects.get(token=token)
            except User.DoesNotExist:
                request.user = None
        else:
            request.user = None

        return self.get_response(request)
