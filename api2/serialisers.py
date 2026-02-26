from rest_framework import serializers
from .models import Car, Owner


class CarSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.name')
    owner_city = serializers.CharField(source='owner.city')

    class Meta:
        model = Car
        fields = ['id', 'make', 'model', 'year', 'owner_name', 'owner_city']


class OwnerSerializer(serializers.ModelSerializer):
    cars = CarSerializer(source='car', many=True)

    class Meta:
        model = Owner
        fields = ['id', 'name', 'city', 'cars']
