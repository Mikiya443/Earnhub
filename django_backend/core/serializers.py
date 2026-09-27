from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task, Transaction, Withdrawal

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","first_name","last_name","email","role","status","wallet_balance","referral_code","date_joined"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    referral_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["username","first_name","last_name","email","password","referral_code"]

    def create(self, validated):
        code = validated.pop("referral_code", "")
        ref = User.objects.filter(referral_code=code).first() if code else None
        password = validated.pop("password")
        user = User(**validated, referred_by=ref)
        user.set_password(password)
        user.save()
        return user

class TaskSerializer(serializers.ModelSerializer):
    completed_today = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = ["id","title","description","reward","daily_limit","active","created_at","completed_today"]
    def get_completed_today(self, obj):
        from django.utils import timezone
        return obj.taskcompletion_set.filter(user=self.context["request"].user, completed_at__date=timezone.localdate()).count()

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id","type","amount","status","reference","description","created_at"]

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ["id","amount","method","account_name","account_number","bank_name","status","note","created_at","processed_at"]
        read_only_fields = ["status","note","processed_at","created_at"]
