from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

def sample_user(email = 'test@dummy.com', password = '12341234'):
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@dummy.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@DUMMY.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'asdf1234')

    def test_create_new_superuser(self):

        user = get_user_model().objects.create_superuser('as@gmail.com', '12341234')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):

        tag = models.Tag.objects.create(
            user=sample_user(),
            name='hydro'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):

        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='vitam'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_drug_str(self):

        drug = models.Drug.objects.create(
            user=sample_user(),
            title='Chloriquien',
            daily_frequency=5,
            price=50.00
        )

        self.assertEqual(str(drug), drug.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.drug_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/drug/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)