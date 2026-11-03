class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.path.startswith('/admin/'):
            response['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-store, private'
        return response
