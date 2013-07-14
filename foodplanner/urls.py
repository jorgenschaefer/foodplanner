from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from recipes.views import MainView
from recipes.views import RecipeListView, RecipeDetailView
from recipes.views import RecipeUpdateView, RecipeDeleteView
from recipes.views import RecipeCreateView
from recipes.views import RandomRecipeView
from recipes.views import IngredientListView, IngredientEditView
from recipes.views import IngredientCreateView, IngredientDeleteView
from recipes.views import IngredientAjaxView, PortionsizeAjaxView
from recipes.views import PortionsizeCreateView, PortionsizeDeleteView
from recipes.views import PortionAddView, PortionDeleteView
from recipes.views import PortionSetAmount, PortionReorderAjaxView


urlpatterns = patterns(
    '',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'foodplanner/login.html'},
        name='auth-login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='auth-logout'),

    url(r'^$', MainView.as_view(),
        name='main'),

    url(r'^ingredients/$', IngredientListView.as_view(),
        name='ingredient-list'),
    url(r'^ingredients/create/$', IngredientCreateView.as_view(),
        name='ingredient-create'),
    url(r'^ingredient/(?P<pk>[0-9]+)/edit/$', IngredientEditView.as_view(),
        name='ingredient-edit'),
    url(r'^ingredient/(?P<pk>[0-9]+)/delete/$', IngredientDeleteView.as_view(),
        name='ingredient-delete'),
    url(r'^ingredient/ajax/$', IngredientAjaxView.as_view(),
        name='ingredient-ajax'),

    url(r'^ingredient/(?P<pk>[0-9]+)/addportionsize/$',
        PortionsizeCreateView.as_view(),
        name='portionsize-create'),
    url(r'^ingredient/(?P<ingredient_id>[0-9]+)/'
        r'deleteportionsize/(?P<pk>[0-9]+)/$',
        PortionsizeDeleteView.as_view(),
        name='portionsize-delete'),
    url(r'^ingredient/portionsize/ajax/$',
        PortionsizeAjaxView.as_view(),
        name='portionsize-ajax'),

    url(r'^recipes/$', RecipeListView.as_view(),
        name='recipe-list'),
    url(r'^recipe/random/$', RandomRecipeView.as_view(),
        name='recipe-random'),
    url(r'^recipe/create/$', RecipeCreateView.as_view(),
        name='recipe-create'),
    url(r'^recipe/(?P<pk>[0-9]+)/$', RecipeDetailView.as_view(),
        name='recipe-detail'),
    url(r'^recipe/(?P<pk>[0-9]+)/edit/$', RecipeUpdateView.as_view(),
        name='recipe-edit'),
    url(r'^recipe/(?P<pk>[0-9]+)/delete/$', RecipeDeleteView.as_view(),
        name='recipe-delete'),

    url(r'^portion/(?P<pk>[0-9]+)/delete/$', PortionDeleteView.as_view(),
        name='portion-delete'),
    url(r'^portion/add/(?P<recipe_id>[0-9]+)/$', PortionAddView.as_view(),
        name='portion-add'),
    url(r'^portion/reorder/$', PortionReorderAjaxView.as_view(),
        name='portion-add'),
    url(r'^portion/(?P<pk>[0-9]+)/setamount/$', PortionSetAmount.as_view(),
        name='portion-set-amount'),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)
