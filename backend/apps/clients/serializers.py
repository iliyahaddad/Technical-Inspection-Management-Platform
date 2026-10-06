from rest_framework import serializers
from apps.clients.models import Client, ClientUser
from apps.accounts.serializers import UserSerializer

class ClientUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ClientUser
        fields = ['id', 'user', 'user_id', 'client', 'role', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']

class ClientSerializer(serializers.ModelSerializer):
    users = ClientUserSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'client_code', 'name', 'trade_name', 'registration_number', 'tax_number', 'address', 'billing_address', 'contact_email', 'contact_phone', 'is_active', 'users', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
