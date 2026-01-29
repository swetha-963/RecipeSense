from django import forms

class IngredientSearchForm(forms.Form):
    ingredients = forms.CharField(
        max_length=500,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter ingredients (e.g., chicken, tomato, rice)',
            'class': 'input-field'
        })
    )
