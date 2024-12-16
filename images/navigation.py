from pages.models import Page
from django.utils.translation import gettext

def get_navigation_items(request):
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

    # Get the current path
    current_path = request.path
    # Assumes LANGUAGE_CODE is in context
    language_prefix = f"/{request.LANGUAGE_CODE}"  
    for item in nav_items:
        item["localized_url"] = f"{language_prefix}{item['url']}"  # Add the locale prefix
        item["is_active"] = current_path == item["localized_url"]  # Mark active item

    return nav_items

