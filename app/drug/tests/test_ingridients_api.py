from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Drug

from drug.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('drug:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the private ingredients API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@dummy.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='xcvb')
        Ingredient.objects.create(user=self.user, name='cbnn')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for the authenticated user are returend"""
        user2 = get_user_model().objects.create_user(
            'other@dummy.com',
            'testpass'
        )
        Ingredient.objects.create(user=user2, name='qqq')
        ingredient = Ingredient.objects.create(user=self.user, name='werwer')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test create a new ingredient"""
        payload = {'name': 'cav'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_drugs(self):
        """Test filtering ingredients by those assigned to drugs"""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Morning')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Evening')
        drug = Drug.objects.create(
            title='Lily drug',
            daily_frequency=10,
            price=5.00,
            user=self.user
        )
        drug.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient = Ingredient.objects.create(user=self.user, name='Breakfast')
        Ingredient.objects.create(user=self.user, name='Lunch')
        drug1 = Drug.objects.create(
            title='Egyptian',
            daily_frequency=5,
            price=3.00,
            user=self.user
        )
        drug1.ingredients.add(ingredient)
        drug2 = Drug.objects.create(
            title='French',
            daily_frequency=3,
            price=2.00,
            user=self.user
        )
        drug2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)