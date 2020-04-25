import tempfile
import os


from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Drug, Tag, Ingredient

from drug.serializers import DrugSerializer, DrugDetailSerializer

DRUGS_URL = reverse('drug:drug-list')

def sample_tag(user, name='Main drug'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='qwer'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)

def detail_url(drug_id):
    """Return drug detail URL"""
    return reverse('drug:drug-detail', args=[drug_id])

def sample_drug(user, **params):
    """Create and return a sample drug"""
    defaults = {
        'title': 'Sample drug',
        'daily_frequency': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Drug.objects.create(user=user, **defaults)


class PublicDrugApiTests(TestCase):
    """Test unauthenticated drug API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(DRUGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDrugApiTests(TestCase):
    """Test unauthenticated drug API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@dummy.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_drugs(self):
        """Test retrieving a list of drugs"""
        sample_drug(user=self.user)
        sample_drug(user=self.user)

        res = self.client.get(DRUGS_URL)

        drugs = Drug.objects.all().order_by('-id')
        serializer = DrugSerializer(drugs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_drugs_limited_to_user(self):
        """Test retrieving drugs for user"""
        user2 = get_user_model().objects.create_user(
            'other@dummy.com',
            'password123'
        )
        sample_drug(user=user2)
        sample_drug(user=self.user)

        res = self.client.get(DRUGS_URL)

        drugs = Drug.objects.filter(user=self.user)
        serializer = DrugSerializer(drugs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_drug_detail(self):
        """Test viewing a drug detail"""
        drug = sample_drug(user=self.user)
        drug.tags.add(sample_tag(user=self.user))
        drug.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(drug.id)
        res = self.client.get(url)

        serializer = DrugDetailSerializer(drug)
        self.assertEqual(res.data, serializer.data)


    def test_create_basic_drug(self):
        """Test creating drugs"""
        payload = {
            'title': 'Blue drug',
            'daily_frequency': 30,
            'price': 5.00
        }
        res = self.client.post(DRUGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        drug = Drug.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(drug, key))

    def test_create_drug_with_tags(self):
        """Test creating a drug with tags"""
        tag1 = sample_tag(user=self.user, name='qwer')
        tag2 = sample_tag(user=self.user, name='weqrwer')
        payload = {
            'title': 'Ninis',
            'tags': [tag1.id, tag2.id],
            'daily_frequency': 6,
            'price': 20.00
        }
        res = self.client.post(DRUGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        drug = Drug.objects.get(id=res.data['id'])
        tags = drug.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_drug_with_ingredients(self):
        """Test creating drug with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='WWEE')
        ingredient2 = sample_ingredient(user=self.user, name='Ginger')
        payload = {
            'title': 'Thai drug',
            'ingredients': [ingredient1.id, ingredient2.id],
            'daily_frequency': 20,
            'price': 7.00
        }
        res = self.client.post(DRUGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        drug = Drug.objects.get(id=res.data['id'])
        ingredients = drug.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_drug(self):
        """Test updating a drug with patch"""
        drug = sample_drug(user=self.user)
        drug.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='new tag')

        payload = {'title': 'Chicken drug', 'tags': [new_tag.id]}
        url = detail_url(drug.id)
        self.client.patch(url, payload)

        drug.refresh_from_db()
        self.assertEqual(drug.title, payload['title'])
        tags = drug.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_drug(self):
        """Test updating a drug with put"""
        drug = sample_drug(user=self.user)
        drug.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'arbon drug',
            'daily_frequency': 25,
            'price': 5.00
        }
        url = detail_url(drug.id)
        self.client.put(url, payload)

        drug.refresh_from_db()
        self.assertEqual(drug.title, payload['title'])
        self.assertEqual(drug.daily_frequency, payload['daily_frequency'])
        self.assertEqual(drug.price, payload['price'])
        tags = drug.tags.all()
        self.assertEqual(len(tags), 0)