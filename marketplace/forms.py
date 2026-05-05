from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Listing, Profile, ROLE_CHOICES, Product, ProductCategory, CartItem, ProductImage


class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs['multiple'] = 'multiple'

    def value_from_datadict(self, data, files, name):
        if name in files:
            return files.getlist(name)
        return []


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = []
            for item in data:
                if item:
                    cleaned = single_file_clean(item, initial)
                    if cleaned:
                        result.append(cleaned)
            return result
        return single_file_clean(data, initial)


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'skill_name', 'description', 'image', 'contact', 'location']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ProductForm(forms.ModelForm):
    images = MultipleFileField(
        required=False,
        help_text='Hold Ctrl (or Cmd) to select multiple images.'
    )

    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'min': '0'}),
        }


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'style': 'width: 80px;'})
    )


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='customer',
        help_text='Customers can buy services and products. Providers offer services. Merchants sell products.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role', 'phone', 'location', 'profile_image']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }
