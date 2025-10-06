from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """Registration form with phone number for M-Pesa"""
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text="Optional: For M-Pesa payments (format: 254XXXXXXXXX)"
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Basic validation for Kenyan numbers
            phone = phone.strip().replace('+', '').replace(' ', '')
            if not phone.startswith('254'):
                raise forms.ValidationError("Phone must start with 254 (e.g., 254712345678)")
            if len(phone) != 12:
                raise forms.ValidationError("Invalid phone number length")
        return phone

class CustomUserLoginForm(AuthenticationForm):
    """Custom login form to apply bootstrap styles"""
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username', 'autofocus': True}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}
    ))