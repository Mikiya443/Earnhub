from django.contrib.auth.models import AbstractUser
from django.db import models
import secrets, string

def referral_code():
    alphabet = string.ascii_uppercase + string.digits
    return "EH-" + "".join(secrets.choice(alphabet) for _ in range(8))

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, default="user")
    status = models.CharField(max_length=20, default="active")
    wallet_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    referral_code = models.CharField(max_length=20, unique=True, default=referral_code)
    referred_by = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="referrals")

    def __str__(self):
        return self.email

class Task(models.Model):
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    reward = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    daily_limit = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TaskCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    TYPES = [
        ("task_reward", "Task reward"), ("deposit", "Deposit"),
        ("withdrawal", "Withdrawal"), ("referral", "Referral"),
        ("adjustment", "Adjustment"),
    ]
    STATUSES = [("pending", "Pending"), ("completed", "Completed"), ("reversed", "Reversed")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=30, choices=TYPES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUSES, default="completed")
    reference = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Withdrawal(models.Model):
    STATUSES = [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdrawals")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    method = models.CharField(max_length=40)
    account_name = models.CharField(max_length=160)
    account_number = models.CharField(max_length=120)
    bank_name = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default="pending")
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
