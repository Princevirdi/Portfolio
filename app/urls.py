from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("resume/", views.resume, name="resume"),
    path("contact/", views.contact, name="contact"),
]
