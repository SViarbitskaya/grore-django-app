from pages.models import Page
from django.utils.translation import gettext

def get_navigation_items():
    # Fetch dynamic pages from the Pages app
    page_items = Page.objects.values('title', 'slug')

    # Static navigation items
    static_navigation_items = [
        {'title': gettext('Home'), 'url': '/'},
        {'title': gettext('Selection'), 'url': '/selection/'},
    ]

    # Combine static and dynamic navigation items
    nav_items = static_navigation_items + [
        {'title': item['title'], 'url': f"/{item['slug']}/"} for item in page_items
    ]

    return nav_items

