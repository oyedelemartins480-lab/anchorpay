from django.db import models
import uuid

class PersistentAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} ({self.id})"
    
class NombaAccount(models.Model):
    persistent_account = models.ForeignKey(
        PersistentAccount,
        on_delete=models.CASCADE,
        related_name='nomba_accounts'
    )
    nomba_account_number = models.CharField(max_length=50)
    nomba_account_reference = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nomba Acct {self.nomba_account_number} -> {self.persistent_account.customer_name}"
    
class Transaction(models.Model):
    persistent_account = models.ForeignKey(
        PersistentAccount,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    nomba_account = models.ForeignKey(
        NombaAccount,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, default='pending')
    raw_webhook_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} -> {self.persistent_account.customer_name} ({self.status})"