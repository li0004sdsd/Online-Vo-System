from django.db import models
from django.contrib.auth.models import User


class Poll(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, '待审核'),
        (STATUS_APPROVED, '已通过'),
        (STATUS_REJECTED, '已删除'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls')
    created_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    allow_multiple = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reject_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='votes')
    voted_at = models.DateTimeField(auto_now_add=True)
    single_vote_key = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [
            ['user', 'poll', 'option'],
            ['user', 'single_vote_key'],
        ]
        ordering = ['-voted_at']

    def __str__(self):
        return f'{self.user.username} voted for {self.option.text}'

    def save(self, *args, **kwargs):
        if self.poll_id and not self.poll.allow_multiple:
            self.single_vote_key = self.poll_id
        else:
            self.single_vote_key = None
        super().save(*args, **kwargs)


class UserActivity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='activity')
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - last active: {self.last_active}'
