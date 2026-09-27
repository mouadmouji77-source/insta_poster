from django import forms

class PostForm(forms.Form):
    image_url = forms.URLField(label='URL de l\'image', required=True)
    caption = forms.CharField(label='Description', widget=forms.Textarea, required=True)
    post_date = forms.DateField(label='Date de publication', required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    post_time = forms.TimeField(label='Heure de publication', required=True, widget=forms.TimeInput(attrs={'type': 'time'}))
