import datetime
import uuid

from django.db import models
from django.db.models import signals
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


class Ingredient(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=128, unique=True)
    kcal = models.FloatField('kcal/100g')
    protein = models.FloatField('Protein/100g')
    carb = models.FloatField('Carb/100g')
    fat = models.FloatField('Fat/100g')
    fiber = models.FloatField('Fiber/100g')

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ingredient-edit', kwargs={'pk': self.id})


def create_gram_portionsize(sender, instance, created, raw, **kwargs):
    if created and not raw:
        PortionSize.objects.create(
            ingredient=instance,
            name="g",
            grams=1)

signals.post_save.connect(create_gram_portionsize,
                          sender=Ingredient)


class PortionSize(models.Model):
    ingredient = models.ForeignKey(Ingredient)
    name = models.CharField(max_length=128)
    grams = models.FloatField()

    class Meta:
        ordering = ["name"]
        unique_together = (("ingredient", "name"),)

    def __unicode__(self):
        return u"{} {}".format(self.name, self.ingredient.name)


def recipe_image_filename(instance, filename):
    now = datetime.datetime.now()
    return (u"images/recipes/{year:4d}/{month:02d}/{uuid}-{filename}"
            .format(year=now.year,
                    month=now.month,
                    uuid=uuid.uuid4(),
                    filename=filename))


class Recipe(models.Model):
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    name = models.CharField(max_length=128, unique=True)
    instructions = models.TextField()
    image = models.ImageField(upload_to=recipe_image_filename,
                              null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.id})

    def nutritionlabel(self):
        if not hasattr(self, '_nutritionlabel'):
            self._nutritionlabel = NutritionLabel(self)
        return self._nutritionlabel


class Portion(models.Model):
    recipe = models.ForeignKey(Recipe)
    amount = models.FloatField()
    portionsize = models.ForeignKey(PortionSize)
    order = models.IntegerField()

    def grams(self):
        return self.amount * self.portionsize.grams

    def kcal(self):
        return (self.grams() * self.portionsize.ingredient.kcal) / 100

    def __unicode__(self):
        return u"{} {}".format(
            self.amount,
            self.portionsize
        )

    class Meta:
        ordering = ["recipe", "order"]


class RecipePortion(models.Model):
    recipe = models.ForeignKey(Recipe)
    amount = models.FloatField()
    subrecipe = models.ForeignKey(Recipe, related_name='superrecipe_set')

    def __unicode__(self):
        return u"{} {}".format(
            self.amount,
            self.subrecipe
        )

    def clean(self):
        super(RecipePortion, self).clean()
        agenda = [self.subrecipe]
        seen = set()
        while agenda:
            this = agenda.pop(0)
            if this == self.recipe:
                raise ValidationError("Can't create recipe cycles")
            if this.id in seen:
                continue
            seen.add(this.id)
            agenda.extend(rp.subrecipe for rp in this.recipeportion_set.all())


class NutritionLabel(object):
    def __init__(self, recipe):
        self.recipe = recipe
        self.grams = 0
        self.kcal = 0
        self.protein = 0
        self.carb = 0
        self.fat = 0
        self.fiber = 0

        for portion in recipe.portion_set.all():
            grams = portion.amount * portion.portionsize.grams
            self.grams += grams
            ingredient = portion.portionsize.ingredient
            self.kcal += (grams * ingredient.kcal) / 100.0
            self.protein += (grams * ingredient.protein) / 100.0
            self.carb += (grams * ingredient.carb) / 100.0
            self.fat += (grams * ingredient.fat) / 100.0
            self.fiber += (grams * ingredient.fiber) / 100.0

        for rp in recipe.recipeportion_set.all():
            subrecipe = rp.subrecipe
            label = subrecipe.nutritionlabel()
            self.grams += label.grams * rp.amount
            self.kcal += label.kcal * rp.amount
            self.protein += label.protein * rp.amount
            self.carb += label.carb * rp.amount
            self.fat += label.fat * rp.amount
            self.fiber += label.fiber * rp.amount

        self.kcal_percent = self.kcal / 2000.0
        if self.kcal_percent > 0.75:
            self.kcal_level = "high"
        else:
            self.kcal_level = "good"

        self.kcal_from_protein = self.protein * 4
        self.kcal_from_carb = self.carb * 4
        self.kcal_from_fat = self.fat * 9
        total_energy = float(self.kcal_from_protein +
                             self.kcal_from_carb +
                             self.kcal_from_fat)
        if total_energy == 0:
            total_energy = 1

        self.protein_percent = self.kcal_from_protein / total_energy
        if self.protein_percent < 0.05:
            self.protein_level = "low"
        elif self.protein_percent > 0.35:
            self.protein_level = "high"
        else:
            self.protein_level = "good"

        self.carb_percent = self.kcal_from_carb / total_energy
        if self.carb_percent < 0.45:
            self.carb_level = "low"
        elif self.carb_percent > 0.60:
            self.carb_level = "high"
        else:
            self.carb_level = "good"

        self.fat_percent = self.kcal_from_fat / total_energy
        if self.fat_percent < 0.20:
            self.fat_level = "low"
        elif self.fat_percent > 0.35:
            self.fat_level = "high"
        else:
            self.fat_level = "good"

        if self.fiber < 25:
            self.fiber_level = "low"
        else:
            self.fiber_level = "good"
