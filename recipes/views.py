from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views import generic
from django.views.generic import edit

from recipes.models import Recipe, Ingredient, PortionSize, Portion
from recipes.forms import IngredientForm, RecipeForm


class MainView(generic.TemplateView):
    template_name = "foodplanner/main.html"

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        qs = Recipe.objects.exclude(
            image=None
        ).exclude(
            image=""
        ).order_by("?")[:3]
        context['recipe_list'] = qs
        return context


from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args,
                                                        **kwargs)


import json
from django.http import HttpResponse


class AjaxMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            if (
                    "application/json" in request.META.get("CONTENT_TYPE",
                                                           "") and
                    request.method in ("POST", "PUT")
            ):
                payload = json.load(request)
                value = super(AjaxMixin, self).dispatch(request, payload,
                                                        *args, **kwargs)
            else:
                value = super(AjaxMixin, self).dispatch(request,
                                                        *args, **kwargs)
            if isinstance(value, HttpResponse):
                return value
            else:
                return HttpResponse(json.dumps(value),
                                    content_type='application/json')
        else:
            return super(AjaxMixin, self).get(*args, **kwargs)


##################################################################
# Ingredient views

class IngredientListView(generic.ListView):
    model = Ingredient
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(IngredientListView, self).get_context_data(**kwargs)
        context['page_ingredientlist'] = True
        return context


class IngredientEditView(LoginRequiredMixin, edit.UpdateView):
    model = Ingredient
    form_class = IngredientForm

    def get_success_url(self):
        return reverse('ingredient-edit', kwargs={'pk': self.object.pk})

    def get_object(self, *args, **kwargs):
        obj = super(IngredientEditView, self).get_object(*args, **kwargs)
        if obj.user != self.request.user:
            raise PermissionDenied()
        return obj

    def get_context_data(self, **kwargs):
        context = super(IngredientEditView, self).get_context_data(**kwargs)
        context['page_ingredientlist'] = True
        context['ingredient_edit'] = True
        return context


class IngredientDeleteView(LoginRequiredMixin, edit.DeleteView):
    model = Ingredient

    def get_success_url(self):
        return reverse('ingredient-list')

    def get_object(self, *args, **kwargs):
        obj = super(IngredientDeleteView, self).get_object(*args, **kwargs)
        if obj.user != self.request.user:
            raise PermissionDenied()
        return obj

    def get_context_data(self, **kwargs):
        context = super(IngredientDeleteView, self).get_context_data(**kwargs)
        context['page_ingredientlist'] = True
        return context


class IngredientCreateView(LoginRequiredMixin, edit.CreateView):
    model = Ingredient
    form_class = IngredientForm

    def get_success_url(self):
        return reverse('ingredient-edit', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        ingredient = form.save(commit=False)
        ingredient.user = self.request.user
        ingredient.save()
        self.object = ingredient
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(IngredientCreateView, self).get_context_data(**kwargs)
        context['page_ingredientlist'] = True
        return context


class IngredientAjaxView(LoginRequiredMixin, AjaxMixin, generic.View):
    def get(self, request):
        return [
            ingredient.name
            for ingredient
            in Ingredient.objects.filter(name__icontains=request.GET['term'])
        ]


##################################################################
# PortionSize views

class PortionsizeCreateView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        ingredient = get_object_or_404(Ingredient, pk=pk)
        PortionSize.objects.get_or_create(
            ingredient=ingredient,
            name=request.POST['name'],
            grams=request.POST['grams'])
        return HttpResponseRedirect(reverse('ingredient-edit',
                                            kwargs={'pk': pk}))


class PortionsizeDeleteView(LoginRequiredMixin, edit.DeleteView):
    model = PortionSize

    def get_success_url(self):
        return reverse('ingredient-edit',
                       kwargs={'pk': self.object.ingredient.pk})

    def get_object(self, *args, **kwargs):
        obj = super(PortionsizeDeleteView, self).get_object(*args, **kwargs)
        if obj.ingredient.user != self.request.user:
            raise PermissionDenied()
        return obj

    def get_context_data(self, **kwargs):
        context = super(PortionsizeDeleteView, self).get_context_data(**kwargs)
        context['page_recipelist'] = True
        return context


class PortionsizeCollectionAjaxView(LoginRequiredMixin, AjaxMixin,
                                    generic.View):
    def get(self, request):
        return [
            {'pk': portionsize.id,
             'label': portionsize.name}
            for portionsize
            in PortionSize.objects.filter(ingredient__name__iexact=
                                          request.GET['ingredient'])
        ]


class PortionsizeAjaxView(LoginRequiredMixin, AjaxMixin, generic.View):
    def put(self, request, obj, pk):
        portionsize = get_object_or_404(PortionSize, pk=pk)
        if portionsize.ingredient.user != request.user:
            raise PermissionDenied()
        if "name" in obj:
            portionsize.name = obj["name"]
        if "grams" in obj:
            try:
                portionsize.grams = float(obj["grams"].replace(",", "."))
            except ValueError:
                pass
        portionsize.save()
        return {"id": portionsize.id,
                "ingradient": portionsize.ingredient.name,
                "name": portionsize.name,
                "grams": portionsize.grams}


class PortionsizeSetNameView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        portionsize = get_object_or_404(PortionSize, pk=pk)
        if portionsize.ingredient.user != request.user:
            raise PermissionDenied()
        portionsize.name = request.POST.get("value")
        portionsize.save()
        return HttpResponseRedirect(
            reverse('ingredient-edit',
                    kwargs={'pk': portionsize.ingredient.id}))


##################################################################
# Recipe views

class RecipeListView(generic.ListView):
    model = Recipe
    paginate_by = 10

    def get_queryset(self):
        if 'q' in self.request.GET:
            return Recipe.objects.filter(name__icontains=self.request.GET['q'])
        else:
            return Recipe.objects.all()

    def get_context_data(self, **kwargs):
        context = super(RecipeListView, self).get_context_data(**kwargs)
        context['page_recipelist'] = True
        if 'q' in self.request.GET:
            context['query'] = self.request.GET['q']
        return context


class RecipeDetailView(generic.DetailView):
    model = Recipe
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super(RecipeDetailView, self).get_context_data(**kwargs)
        context['page_recipelist'] = True
        return context


class RecipeDeleteView(LoginRequiredMixin, edit.DeleteView):
    model = Recipe

    def get_success_url(self):
        return reverse('recipe-list')

    def get_object(self, *args, **kwargs):
        obj = super(RecipeDeleteView, self).get_object(*args, **kwargs)
        if obj.user != self.request.user:
            raise PermissionDenied()
        return obj

    def get_context_data(self, **kwargs):
        context = super(RecipeDeleteView, self).get_context_data(**kwargs)
        context['page_recipelist'] = True
        return context


class RecipeUpdateView(edit.UpdateView):
    model = Recipe
    form_class = RecipeForm

    def get_object(self, *args, **kwargs):
        obj = super(RecipeUpdateView, self).get_object(*args, **kwargs)
        if obj.user != self.request.user:
            raise PermissionDenied()
        return obj

    def get_context_data(self, **kwargs):
        context = super(RecipeUpdateView, self).get_context_data(**kwargs)
        context['page_recipelist'] = True
        context['recipe_edit'] = True
        return context


class RecipeCreateView(LoginRequiredMixin, edit.CreateView):
    model = Recipe
    form_class = RecipeForm

    def form_valid(self, form):
        recipe = form.save(commit=False)
        recipe.user = self.request.user
        recipe.save()
        self.object = recipe
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(RecipeCreateView, self).get_context_data(**kwargs)
        context['page_recipelist'] = True
        return context


class RandomRecipeView(generic.RedirectView):
    permanent = False

    def get_redirect_url(self):
        try:
            r = Recipe.objects.order_by("?")[0]
        except IndexError:
            return "/"
        return r.get_absolute_url()


##################################################################
# Portion views

class PortionDeleteView(LoginRequiredMixin, edit.DeleteView):
    model = Portion

    def get_success_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.object.recipe.pk})

    def get_object(self, *args, **kwargs):
        obj = super(PortionDeleteView, self).get_object(*args, **kwargs)
        if obj.recipe.user != self.request.user:
            raise PermissionDenied()
        return obj

    def get_context_data(self, **kwargs):
        context = super(PortionDeleteView, self).get_context_data(**kwargs)
        context['page_recipelist'] = True
        return context


class PortionAddView(LoginRequiredMixin, generic.View):
    def post(self, request, recipe_id):
        destination = HttpResponseRedirect(reverse('recipe-detail',
                                                   kwargs={'pk': recipe_id}))
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        try:
            ingredient = Ingredient.objects.get(
                user=request.user,
                name=request.POST['ingredient'])
        except Ingredient.DoesNotExist:
            return destination
        try:
            portionsize = PortionSize.objects.get(
                ingredient=ingredient,
                pk=request.POST['portionsize'])
        except PortionSize.DoesNotExist:
            return destination

        if recipe.portion_set.count() > 0:
            order = (max(p.order for p in recipe.portion_set.all()) +
                     1)
        else:
            order = 0

        Portion.objects.create(
            recipe=recipe,
            portionsize=portionsize,
            order=order,
            amount=request.POST['amount'])
        return destination


class PortionAjaxView(LoginRequiredMixin, AjaxMixin, generic.View):
    def put(self, request, obj, pk):
        portion = get_object_or_404(Portion, pk=pk)
        if portion.recipe.user != request.user:
            raise PermissionDenied()
        try:
            portion.amount = float(obj["amount"].replace(",", "."))
        except ValueError:
            pass
        else:
            portion.save()
        return {"id": portion.id,
                "amount": portion.amount}


class PortionReorderAjaxView(LoginRequiredMixin, AjaxMixin, generic.View):
    def post(self, request):
        recipe = None
        new_order = json.loads(request.POST.get('neworder', '[]'))
        for i, pk in enumerate(new_order):
            try:
                portion = Portion.objects.get(pk=pk)
            except Portion.DoesNotExist:
                return False
            if portion.recipe.user != request.user:
                return False
            if recipe is None:
                recipe = portion.recipe
            elif recipe != portion.recipe:
                return False
            portion.order = i
            portion.save()
        return True
