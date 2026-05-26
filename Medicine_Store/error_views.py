from django.shortcuts import render


def page_not_found(request, exception=None, **kwargs):
    """Custom 404 page for missing URLs."""
    return render(request, 'errors/404.html', status=404)


def server_error(request, **kwargs):
    """Custom 500 page for server errors."""
    return render(request, 'errors/500.html', status=500)


def connection_error(request):
    """Shown when email, payment, or external services fail due to connectivity."""
    return render(request, 'errors/connection_error.html', status=503)
