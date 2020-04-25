from django.urls import path, include
from rest_framework.routers import DefaultRouter

from drug import views


router = DefaultRouter()

router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('drugs', views.DrugViewSet)


app_name = 'drug'

urlpatterns = [
    path('', include(router.urls))
]