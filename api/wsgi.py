import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portfolio.settings")


def _bootstrap_django_for_vercel() -> None:
    """
    Vercel serverless instances are effectively ephemeral.
    If you're using SQLite, the deployed instance may not have run migrations
    or created the admin user yet, so `/admin/` can fail.
    """

    # Optional: you can disable this if you don't want migrations at cold start.
    if os.environ.get("DJANGO_AUTO_MIGRATE", "1") != "1":
        return

    # Ensure Django is initialized before using management/model APIs.
    import django

    django.setup()

    from django.contrib.auth import get_user_model
    from django.core.management import call_command

    print("[django vercel bootstrap] starting")

    # Apply migrations so auth/admin tables exist.
    call_command("migrate", interactive=False, verbosity=0)
    print("[django vercel bootstrap] migrate complete")

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
            print("[django vercel bootstrap] superuser created:", username)
        else:
            user.set_password(password)
            # Ensure admin login works even if the account existed previously
            # but wasn't flagged as staff/superuser.
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            # Save all fields to avoid any edge-cases with update_fields.
            user.save()
            print("[django vercel bootstrap] superuser updated:", username)


_bootstrap_django_for_vercel()

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
