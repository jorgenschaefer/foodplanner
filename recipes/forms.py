from django import forms

from recipes import models


class IngredientForm(forms.ModelForm):
    class Meta:
        model = models.Ingredient
        fields = ['name', 'kcal', 'protein', 'carb', 'fat', 'fiber', 'isfluid']


class RecipeForm(forms.ModelForm):
    class Meta:
        model = models.Recipe
        fields = ['name', 'instructions', 'image']
