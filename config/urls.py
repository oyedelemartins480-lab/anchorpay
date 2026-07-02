from django.contrib import admin
from django.urls import path
from accounts.views import (
    nomba_webhook,
    create_account_view,
    get_account_view,
    list_accounts_view,
    dashboard_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhooks/nomba/', nomba_webhook),
    path('api/accounts/', create_account_view),
    path('api/accounts/list/', list_accounts_view),
    path('api/accounts/<uuid:account_id>/', get_account_view),
    path('', dashboard_view),
]