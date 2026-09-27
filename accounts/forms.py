from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    access_token = forms.CharField(
        max_length=255,
        required=False,
        label='Access Token',
        widget=forms.TextInput()
    )
    instagram_page_id = forms.CharField(
        max_length=255,
        required=False,
        label='Instagram Page ID',
        widget=forms.TextInput()
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'access_token', 'instagram_page_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            field.help_text = None  # Optional: remove default help texts

    def save(self, commit=True):
        user = super().save(commit=False)
        user.access_token = self.cleaned_data.get('access_token')
        user.instagram_page_id = self.cleaned_data.get('instagram_page_id')
        if commit:
            user.save()
        return user

class UpdateUserForm(UserChangeForm):
    password1 = forms.CharField(
        label='New Password',
        max_length=128,
        required=False,
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label='Confirm New Password',
        max_length=128,
        required=False,
        widget=forms.PasswordInput()
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'access_token', 'instagram_page_id', 'password1', 'password2']
        exclude = ('password',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the initial password field
        self.fields.pop('password', None)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            field.help_text = None  # Optional: remove default help texts

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
