from django.shortcuts import render

from .forms import ContactMessageForm


def home(request):
    return render(request, "index.html")


def about(request):
    return render(request, "index.html")


def portfolio(request):
    return render(request, "portfolio.html")


def resume(request):
    return render(request, "resume.html")


def contact(request):
    success = False
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            form = ContactMessageForm()
    else:
        form = ContactMessageForm()

    return render(request, "contact.html", {"form": form, "success": success})
