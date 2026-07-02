from rest_framework import serializers
from .models import PersistentAccount, NombaAccount, Transaction


class NombaAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = NombaAccount
        fields = ['nomba_account_number', 'is_active', 'created_at', 'expires_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'reference', 'status', 'created_at']


class PersistentAccountSerializer(serializers.ModelSerializer):
    nomba_accounts = NombaAccountSerializer(many=True, read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = PersistentAccount
        fields = [
            'id', 'customer_name', 'customer_email', 'balance',
            'created_at', 'nomba_accounts', 'transactions',
        ]