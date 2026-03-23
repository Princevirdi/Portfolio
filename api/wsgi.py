import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portfolio.settings")


def _bootstrap_django_for_vercel() -> None:
    """
    Vercel serverless instances are effectively ephemeral.
    If you're using SQLite, the deployed instance may not have run migrations
    or created the admin user yet, so `/admin/` can fail.
    """

    # Only bootstrap on Vercel (keeps local dev behavior predictable).
    if not os.environ.get("VERCEL"):
        return

    # Optional: you can disable this if you don't want migrations at cold start.
    if os.environ.get("DJANGO_AUTO_MIGRATE", "1") != "1":
        return

    # Ensure Django is initialized before using management/model APIs.
    import django

    django.setup()

    from django.contrib.auth import get_user_model
    from django.core.management import call_command

    # Apply migrations so auth/admin tables exist.
    call_command("migrate", interactive=False, verbosity=0)

    # Optionally create a superuser for admin access.
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    if username and password:
        User = get_user_model()
        user = User.objects.filter(username=username).first()

        # If the user already exists (e.g., from a previous deploy),
        # ensure the password matches the current env var.
        if user is None:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
        else:
            user.set_password(password)
            # Avoid triggering extra validation; `set_password` sets hash.
            user.save(update_fields=["password"])


_bootstrap_django_for_vercel()

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
