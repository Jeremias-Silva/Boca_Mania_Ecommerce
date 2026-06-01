from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Product, CustomerProfile

# 🛒 PRODUCTS
class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [
            'name',
            'price',
            'description',
            'image',
            'stock'
        ]

        # ✅ FORM STYLING
        widgets = {

            'name': forms.TextInput(attrs={
                'class': 'form-control boca-input',
                'placeholder': 'Product Name'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control boca-input',
                'placeholder': 'Product Description'
            }),

            'price': forms.NumberInput(attrs={
                'class': 'form-control boca-input',
                'placeholder': 'Price'
            }),

            'stock': forms.NumberInput(attrs={
                'class': 'form-control boca-input',
                'placeholder': 'Stock Quantity'
            }),

            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control boca-input'
            }),
        }


# 👤 REGISTER
class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control boca-input',
            'placeholder': 'Email'
        })
    )

    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control boca-input',
            'placeholder': 'City'
        })
    )

    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control boca-input',
            'placeholder': 'Address'
        })
    )

    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control boca-input',
            'placeholder': 'Phone Number'
        })
    )

    class Meta:

        model = User

        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]

        widgets = {

            'username': forms.TextInput(attrs={
                'class': 'form-control boca-input',
                'placeholder': 'Username'
            }),
        }

    # ✅ PASSWORD FIELD STYLING
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control boca-input',
            'placeholder': 'Password'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control boca-input',
            'placeholder': 'Confirm Password'
        })
    )

    def save(self, commit=True):

        user = super().save(commit=False)

        # save email
        user.email = self.cleaned_data['email']

        if commit:

            user.save()

            # create customer profile
            CustomerProfile.objects.create(
                user=user,
                city=self.cleaned_data['city'],
                address=self.cleaned_data['address'],
                phone=self.cleaned_data['phone']
            )

        return user