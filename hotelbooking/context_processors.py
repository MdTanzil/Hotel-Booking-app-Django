"""Context processors for the hotelbooking app."""

from django.db import OperationalError, ProgrammingError


def site_settings(request):
    """Make the single SiteSettings row available as ``site_settings``.

    Returns None when the table has no row yet, or the table does not
    exist (e.g. before migrations run); templates fall back to hardcoded
    defaults in that case, so pages never crash.
    """
    try:
        from .models import SiteSettings

        return {"site_settings": SiteSettings.get_settings()}
    except (OperationalError, ProgrammingError):
        return {"site_settings": None}
