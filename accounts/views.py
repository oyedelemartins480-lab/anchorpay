import json
import os
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import NombaAccount, Transaction, PersistentAccount
from .serializers import PersistentAccountSerializer
from .nomba_client import create_persistent_account
from django.shortcuts import render


def check_api_key(request):
    key = request.headers.get('X-API-Key')
    if key != os.getenv('ANCHORPAY_API_KEY'):
        return False
    return True


@csrf_exempt
def nomba_webhook(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    payload = json.loads(request.body)

    event_type = payload.get("event_type")

    if event_type != "payment_success":
        return JsonResponse({"status": "ignored, not a payment event"}, status=200)

    transaction_data = payload["data"]["transaction"]
    account_number = transaction_data["aliasAccountNumber"]
    amount = Decimal(str(transaction_data["transactionAmount"]))
    reference = transaction_data["transactionId"]

    try:
        nomba_account = NombaAccount.objects.get(
            nomba_account_number=account_number,
            is_active=True,
        )
    except NombaAccount.DoesNotExist:
        return JsonResponse(
            {"error": "No matching active account found"}, status=404
        )

    if Transaction.objects.filter(reference=reference).exists():
        return JsonResponse({"status": "already processed"}, status=200)

    Transaction.objects.create(
        persistent_account=nomba_account.persistent_account,
        nomba_account=nomba_account,
        amount=amount,
        reference=reference,
        status="completed",
        raw_webhook_payload=payload,
    )

    persistent_account = nomba_account.persistent_account
    persistent_account.balance += amount
    persistent_account.save()

    return JsonResponse({"status": "processed"}, status=200)


@api_view(['POST'])
def create_account_view(request):
    if not check_api_key(request):
        return Response({"error": "Invalid or missing API key"}, status=401)

    customer_name = request.data.get('customer_name')
    customer_email = request.data.get('customer_email')

    if not customer_name or not customer_email:
        return Response(
            {"error": "customer_name and customer_email are required"},
            status=400,
        )

    account = create_persistent_account(customer_name, customer_email)
    serializer = PersistentAccountSerializer(account)
    return Response(serializer.data, status=201)


@api_view(['GET'])
def get_account_view(request, account_id):
    if not check_api_key(request):
        return Response({"error": "Invalid or missing API key"}, status=401)

    try:
        account = PersistentAccount.objects.get(id=account_id)
    except PersistentAccount.DoesNotExist:
        return Response({"error": "Account not found"}, status=404)

    serializer = PersistentAccountSerializer(account)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def list_accounts_view(request):
    if not check_api_key(request):
        return Response({"error": "Invalid or missing API key"}, status=401)

    accounts = PersistentAccount.objects.all()
    serializer = PersistentAccountSerializer(accounts, many=True)
    return Response(serializer.data, status=200)
def dashboard_view(request):
    accounts = PersistentAccount.objects.all().order_by('-created_at')
    return render(request, 'dashboard.html', {'accounts': accounts})