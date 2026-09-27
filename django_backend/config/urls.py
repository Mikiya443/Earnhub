from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from core.views import RegisterView, MeView, DashboardView, TaskListView, TaskCompleteView, WalletView, TransactionListView, WithdrawalCreateView, ReferralView, AdminStatsView, AdminUsersView, AdminUserStatusView, AdminWithdrawalsView, AdminWithdrawalActionView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/login/", __import__("rest_framework_simplejwt.views", fromlist=["TokenObtainPairView"]).TokenObtainPairView.as_view()),
    path("api/auth/refresh/", TokenRefreshView.as_view()),
    path("api/auth/me/", MeView.as_view()),
    path("api/dashboard/", DashboardView.as_view()),
    path("api/tasks/", TaskListView.as_view()),
    path("api/tasks/<int:pk>/complete/", TaskCompleteView.as_view()),
    path("api/wallet/", WalletView.as_view()),
    path("api/wallet/transactions/", TransactionListView.as_view()),
    path("api/wallet/withdraw/", WithdrawalCreateView.as_view()),
    path("api/referrals/", ReferralView.as_view()),
    path("api/admin/stats/", AdminStatsView.as_view()),
    path("api/admin/users/", AdminUsersView.as_view()),
    path("api/admin/users/<int:pk>/status/", AdminUserStatusView.as_view()),
    path("api/admin/withdrawals/", AdminWithdrawalsView.as_view()),
    path("api/admin/withdrawals/<int:pk>/action/", AdminWithdrawalActionView.as_view()),
]
