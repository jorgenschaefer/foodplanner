from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from recipes import views


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

    url(r'^$', views.MainView.as_view(),
        name='main'),

    url(r'^ingredients/$', views.IngredientListView.as_view(),
        name='ingredient-list'),
    url(r'^ingredients/create/$', views.IngredientCreateView.as_view(),
        name='ingredient-create'),
    url(r'^ingredient/(?P<pk>[0-9]+)/edit/$',
        views.IngredientEditView.as_view(),
        name='ingredient-edit'),
    url(r'^ingredient/(?P<pk>[0-9]+)/delete/$',
        views.IngredientDeleteView.as_view(),
        name='ingredient-delete'),
    url(r'^api/ingredient/$', views.IngredientAjaxView.as_view(),
        name='ingredient-ajax'),

    url(r'^ingredient/(?P<pk>[0-9]+)/addportionsize/$',
        views.PortionsizeCreateView.as_view(),
        name='portionsize-create'),
    url(r'^ingredient/(?P<ingredient_id>[0-9]+)/'
        r'deleteportionsize/(?P<pk>[0-9]+)/$',
        views.PortionsizeDeleteView.as_view(),
        name='portionsize-delete'),
    url(r'^api/portionsize/$',
        views.PortionsizeCollectionAjaxView.as_view(),
        name='portionsize-ajax'),
    url(r'^api/portionsize/(?P<pk>[0-9]+)/$',
        views.PortionsizeAjaxView.as_view(),
        name='portionsize-put'),

    url(r'^recipes/$', views.RecipeListView.as_view(),
        name='recipe-list'),
    url(r'^recipe/random/$', views.RandomRecipeView.as_view(),
        name='recipe-random'),
    url(r'^recipe/create/$', views.RecipeCreateView.as_view(),
        name='recipe-create'),
    url(r'^recipe/(?P<pk>[0-9]+)/$', views.RecipeDetailView.as_view(),
        name='recipe-detail'),
    url(r'^recipe/(?P<pk>[0-9]+)/edit/$', views.RecipeUpdateView.as_view(),
        name='recipe-edit'),
    url(r'^recipe/(?P<pk>[0-9]+)/delete/$', views.RecipeDeleteView.as_view(),
        name='recipe-delete'),

    url(r'^portion/(?P<pk>[0-9]+)/delete/$', views.PortionDeleteView.as_view(),
        name='portion-delete'),
    url(r'^portion/add/(?P<recipe_id>[0-9]+)/$',
        views.PortionAddView.as_view(),
        name='portion-add'),
    url(r'^api/portion/reorder/$', views.PortionReorderAjaxView.as_view(),
        name='portion-add'),
    url(r'^api/portion/(?P<pk>[0-9]+)/$',
        views.PortionAjaxView.as_view(),
        name='portion-put'),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)
