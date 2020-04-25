from rest_framework import serializers

from core.models import Tag, Ingredient, Drug


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class DrugSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Drug
        fields = ('id', 'title')
        read_only_fields = ('id',)

class DrugSerializer(serializers.ModelSerializer):
    """Serialize a recipe"""
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Drug
        fields = (
            'id', 'title', 'ingredients', 'tags', 'daily_frequency',
            'price', 'link'
        )
        read_only_fields = ('id',)

class DrugDetailSerializer(DrugSerializer):
    """Serialize a recipe detail"""
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
