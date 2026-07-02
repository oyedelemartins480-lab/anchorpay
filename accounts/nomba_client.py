import requests
import os

NOMBA_BASE_URL = os.getenv('NOMBA_BASE_URL')
NOMBA_CLIENT_ID = os.getenv('NOMBA_CLIENT_ID')
NOMBA_PRIVATE_KEY = os.getenv('NOMBA_PRIVATE_KEY')
NOMBA_ACCOUNT_ID = os.getenv('NOMBA_ACCOUNT_ID')


def get_access_token():
    """
    Asks Nomba for a temporary access token using our client credentials.
    This token is what we'll attach to every other request we make.
    """
    url = f"{NOMBA_BASE_URL}/v1/auth/token/issue"
    headers = {
        "Content-Type": "application/json",
        "accountId": NOMBA_ACCOUNT_ID,
    }
    payload = {
        "grant_type": "client_credentials",
        "client_id": NOMBA_CLIENT_ID,
        "client_secret": NOMBA_PRIVATE_KEY,
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data["data"]["access_token"]

import uuid


def create_virtual_account(account_name, bvn="12345678901"):
    """
    Creates a new virtual account on Nomba, tied to a given account name.
    Returns the account details Nomba gives back (account number, bank name, etc.)
    """
    token = get_access_token()

    account_ref = str(uuid.uuid4())

    url = f"{NOMBA_BASE_URL}/v1/accounts/virtual"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "accountId": NOMBA_ACCOUNT_ID,
    }
    payload = {
        "accountRef": account_ref,
        "accountName": account_name,
        "bvn": bvn,
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    return response.json()["data"]

from .models import PersistentAccount, NombaAccount


def create_persistent_account(customer_name, customer_email, bvn="12345678901"):
    """
    The main function AnchorPay is built around:
    1. Creates a real (sandbox) virtual account on Nomba
    2. Creates our own permanent PersistentAccount record
    3. Links them together via a NombaAccount record
    """
    nomba_data = create_virtual_account(customer_name, bvn)

    persistent_account = PersistentAccount.objects.create(
        customer_name=customer_name,
        customer_email=customer_email,
    )

    NombaAccount.objects.create(
        persistent_account=persistent_account,
        nomba_account_number=nomba_data['bankAccountNumber'],
        nomba_account_reference=nomba_data['accountRef'],
        is_active=True,
    )

    return persistent_account
from django.utils import timezone
from datetime import timedelta


def renew_account_if_needed(nomba_account, days_before_expiry=2):
    """
    Checks if a NombaAccount is close to expiring (or has no expiry set yet).
    If so, creates a new Nomba account and remaps it to the same
    PersistentAccount — the customer's permanent identity never changes.
    """
    if nomba_account.expires_at is None:
        return None

    time_until_expiry = nomba_account.expires_at - timezone.now()

    if time_until_expiry > timedelta(days=days_before_expiry):
        return None

    persistent_account = nomba_account.persistent_account

    nomba_data = create_virtual_account(persistent_account.customer_name)

    nomba_account.is_active = False
    nomba_account.save()

    new_nomba_account = NombaAccount.objects.create(
        persistent_account=persistent_account,
        nomba_account_number=nomba_data['bankAccountNumber'],
        nomba_account_reference=nomba_data['accountRef'],
        is_active=True,
    )

    return new_nomba_account