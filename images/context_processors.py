# context_processors.py
from .navigation import get_navigation_items

def navigation_context(request):
    return {
        'navigation_items': get_navigation_items()
    }
