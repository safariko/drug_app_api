from django.urls import path, include
from rest_framework.routers import DefaultRouter

from drug import views


router = DefaultRouter()

router.register('tags', views.TagViewSet)


app_name = 'drug'

urlpatterns = [
    path('', include(router.urls))
]