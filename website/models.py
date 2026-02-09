from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course = models.CharField(max_length=100,blank=True)
    subjects = models.JSONField(default=list, blank=True)
    levels = models.JSONField(default=dict, blank=True)
    semester = models.CharField(max_length=2, blank=True, null=True)
    study_level = models.JSONField(default=dict, blank=True)
    availability = models.CharField(
    max_length=100,
    default="Not specified"
)

    study_hours = models.IntegerField(default=4)

    def __str__(self):
        return self.user.username


class StudyBuddyRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_requests'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_requests'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.status})"

class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="matches_as_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="matches_as_user2")
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user1", "user2")
from django.db import models
from django.contrib.auth.models import User


class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    score = models.IntegerField()
    total = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def percentage(self):
        if self.total == 0:
            return 0
        return int((self.score / self.total) * 100)

