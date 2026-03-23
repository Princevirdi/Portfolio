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
    from django.conf import settings as django_settings

    print("[django vercel bootstrap] starting")

    try:
        # In serverless environments the filesystem is ephemeral and can be
        # accessed concurrently. For SQLite, we avoid running migrations if
        # the DB file already exists (unless explicitly forced).
        db_name = str(django_settings.DATABASES["default"]["NAME"])
        force_migrate = os.environ.get("DJANGO_FORCE_MIGRATE", "0") == "1"
        reset_db = os.environ.get("DJANGO_RESET_DB", "0") == "1"

        if reset_db and os.path.exists(db_name):
            try:
                os.remove(db_name)
                print("[django vercel bootstrap] db reset: removed", db_name)
            except Exception as exc:
                print("[django vercel bootstrap] db reset failed:", repr(exc))

        db_missing = not os.path.exists(db_name)
        print(
            "[django vercel bootstrap] db_path=",
            db_name,
            "force_migrate=",
            force_migrate,
            "reset_db=",
            reset_db,
            "db_missing=",
            db_missing,
        )

        if force_migrate or db_missing:
            # Apply migrations so auth/admin tables exist.
            call_command("migrate", interactive=False, verbosity=0)
            print("[django vercel bootstrap] migrate complete")
        else:
            print("[django vercel bootstrap] migrate skipped (db exists)")

        # Create/update a superuser for admin access.
        username = (os.environ.get("DJANGO_SUPERUSER_USERNAME") or "").strip()
        email = (os.environ.get("DJANGO_SUPERUSER_EMAIL") or "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        print(
            "[django vercel bootstrap] superuser env: username_set=",
            bool(username),
            "email_set=",
            bool(email),
            "password_set=",
            bool(password),
            "username=",
            username,
        )

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
