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

    try:
        # Apply migrations so auth/admin tables exist.
        call_command("migrate", interactive=False, verbosity=0)
        print("[django vercel bootstrap] migrate complete")

        # Create/update a superuser for admin access.
        username = (os.environ.get("DJANGO_SUPERUSER_USERNAME") or "").strip()
        email = (os.environ.get("DJANGO_SUPERUSER_EMAIL") or "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if username and password:
            User = get_user_model()
            username_field = getattr(User, "USERNAME_FIELD", "username")

            lookup = {f"{username_field}__iexact": username}
            user = User.objects.filter(**lookup).first()

            if user is None:
                # Use create_superuser to ensure proper flags.
                user_kwargs = {username_field: username}
                user_kwargs.update({"email": email, "password": password})
                user = User.objects.create_superuser(**user_kwargs)
                print("[django vercel bootstrap] superuser created:", username)
            else:
                user.set_password(password)
                # Ensure admin login works even if the account existed previously
                # but wasn't flagged as staff/superuser.
                if hasattr(user, "is_staff"):
                    user.is_staff = True
                if hasattr(user, "is_superuser"):
                    user.is_superuser = True
                if hasattr(user, "is_active"):
                    user.is_active = True
                user.save()
                print(
                    "[django vercel bootstrap] superuser updated:",
                    username,
                    "is_staff=",
                    getattr(user, "is_staff", None),
                    "is_superuser=",
                    getattr(user, "is_superuser", None),
                )
        else:
            print(
                "[django vercel bootstrap] missing env vars:",
                "DJANGO_SUPERUSER_USERNAME=",
                bool(username),
                "DJANGO_SUPERUSER_PASSWORD=",
                bool(password),
            )
    except Exception as exc:
        # Print the error so it shows up in Vercel logs.
        print("[django vercel bootstrap] error:", repr(exc))


_bootstrap_django_for_vercel()

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
