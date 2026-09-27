import uuid
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Task, TaskCompletion, Transaction, Withdrawal
from .serializers import UserSerializer, RegisterSerializer, TaskSerializer, TransactionSerializer, WithdrawalSerializer

User = get_user_model()

def token_pair(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data); s.is_valid(raise_exception=True)
        user = s.save()
        return Response({"user": UserSerializer(user).data, "tokens": token_pair(user)}, status=201)

class MeView(APIView):
    def get(self, request): return Response({"user": UserSerializer(request.user).data})

class DashboardView(APIView):
    def get(self, request):
        return Response({
            "user": UserSerializer(request.user).data,
            "recent_transactions": TransactionSerializer(request.user.transactions.order_by("-id")[:8], many=True).data,
            "tasks_available": Task.objects.filter(active=True).count(),
            "referrals": request.user.referrals.count(),
        })

class TaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    def get_queryset(self): return Task.objects.filter(active=True).order_by("-id")

class TaskCompleteView(APIView):
    def post(self, request, pk):
        with transaction.atomic():
            task = Task.objects.select_for_update().filter(pk=pk, active=True).first()
            if not task: return Response({"error":"Task not found"}, status=404)
            today = timezone.localdate()
            count = TaskCompletion.objects.filter(user=request.user, task=task, completed_at__date=today).count()
            if count >= task.daily_limit:
                return Response({"error":"Daily task limit reached"}, status=400)
            TaskCompletion.objects.create(user=request.user, task=task)
            user = User.objects.select_for_update().get(pk=request.user.pk)
            user.wallet_balance += task.reward
            user.save(update_fields=["wallet_balance"])
            Transaction.objects.create(user=user, type="task_reward", amount=task.reward, status="completed", reference="TASK-"+uuid.uuid4().hex[:16], description=f"Reward for {task.title}")
        return Response({"message":"Task completed","reward":task.reward})

class WalletView(APIView):
    def get(self, request): return Response({"balance": request.user.wallet_balance})

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    def get_queryset(self): return Transaction.objects.filter(user=self.request.user).order_by("-id")[:100]

class WithdrawalCreateView(generics.CreateAPIView):
    serializer_class = WithdrawalSerializer
    def perform_create(self, serializer):
        amount = Decimal(self.request.data.get("amount", "0"))
        if amount <= 0: raise ValueError("Invalid amount")
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=self.request.user.pk)
            if user.wallet_balance < amount: raise ValueError("Insufficient wallet balance")
            user.wallet_balance -= amount
            user.save(update_fields=["wallet_balance"])
            withdrawal = serializer.save(user=user, amount=amount)
            Transaction.objects.create(user=user, type="withdrawal", amount=amount, status="pending", reference="WD-"+uuid.uuid4().hex[:16], description=f"Withdrawal #{withdrawal.id}")

class ReferralView(APIView):
    def get(self, request):
        refs = request.user.referrals.order_by("-id").values("id","username","email","date_joined","status")
        return Response({"referral_code":request.user.referral_code,"referrals":list(refs)})

def admin_only(request):
    return request.user.is_staff or request.user.role == "admin"

class AdminStatsView(APIView):
    def get(self, request):
        if not admin_only(request): return Response({"error":"Admin access required"}, status=403)
        return Response({
            "users": User.objects.count(),
            "active_users": User.objects.filter(status="active").count(),
            "pending_withdrawals": Withdrawal.objects.filter(status="pending").count(),
            "pending_amount": Withdrawal.objects.filter(status="pending").aggregate_total if False else sum(Withdrawal.objects.filter(status="pending").values_list("amount", flat=True), Decimal("0")),
        })

class AdminUsersView(APIView):
    def get(self, request):
        if not admin_only(request): return Response({"error":"Admin access required"}, status=403)
        return Response({"users":UserSerializer(User.objects.order_by("-id")[:500],many=True).data})

class AdminUserStatusView(APIView):
    def patch(self, request, pk):
        if not admin_only(request): return Response({"error":"Admin access required"}, status=403)
        user = User.objects.filter(pk=pk).first()
        if not user: return Response({"error":"User not found"},status=404)
        if request.data.get("status") not in ["active","suspended"]: return Response({"error":"Invalid status"},status=400)
        user.status=request.data["status"]; user.save(update_fields=["status"])
        return Response({"message":"Updated"})

class AdminWithdrawalsView(APIView):
    def get(self, request):
        if not admin_only(request): return Response({"error":"Admin access required"}, status=403)
        return Response({"withdrawals":WithdrawalSerializer(Withdrawal.objects.select_related("user").order_by("-id")[:500],many=True).data})

class AdminWithdrawalActionView(APIView):
    def patch(self, request, pk):
        if not admin_only(request): return Response({"error":"Admin access required"}, status=403)
        with transaction.atomic():
            w = Withdrawal.objects.select_for_update().select_related("user").filter(pk=pk).first()
            if not w: return Response({"error":"Not found"},status=404)
            if w.status != "pending": return Response({"error":"Already processed"},status=400)
            action=request.data.get("status")
            if action not in ["approved","rejected"]: return Response({"error":"Invalid status"},status=400)
            if action=="rejected":
                user=User.objects.select_for_update().get(pk=w.user_id)
                user.wallet_balance += w.amount; user.save(update_fields=["wallet_balance"])
            w.status=action; w.note=request.data.get("note",""); w.processed_at=timezone.now(); w.save()
            Transaction.objects.filter(user=w.user,type="withdrawal",status="pending",description=f"Withdrawal #{w.id}").update(status="completed" if action=="approved" else "reversed")
        return Response({"message":action})
