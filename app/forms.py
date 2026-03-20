from django import forms

from .models import ContactMessage


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Your name", "autocomplete": "name"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "you@email.com", "autocomplete": "email"}
            ),
            "subject": forms.TextInput(attrs={"placeholder": "Project inquiry"}),
            "message": forms.Textarea(attrs={"rows": 5, "placeholder": "Tell me about your idea..."}),
        }
