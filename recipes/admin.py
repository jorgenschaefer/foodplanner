from django.contrib import admin
from recipes.models import Ingredient
from recipes.models import PortionSize, Portion, RecipePortion
from recipes.models import Recipe

admin.site.register(Ingredient)
admin.site.register(PortionSize)


class PortionAdmin(admin.TabularInline):
    model = Portion


class RecipePortionAdmin(admin.TabularInline):
    model = RecipePortion
    fk_name = 'recipe'
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        PortionAdmin,
        RecipePortionAdmin,
    ]

admin.site.register(Recipe, RecipeAdmin)
