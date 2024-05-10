from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
import os

import string
from random import sample


class CodeGenerate(models.Model):
    code = models.CharField(max_length=255, blank=True,unique=True)
    @staticmethod
    def generate_code():
        return ''.join(sample(string.ascii_letters + string.digits, 15)) 
    
    def save(self, *args, **kwargs):
        if not self.id:
            while True:
                code = self.generate_code()
                if not self.__class__.objects.filter(code=code).count():
                    self.code = code
                    break
        super(CodeGenerate,self).save(*args, **kwargs)

    class Meta:
        abstract = True


class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    bio = models.TextField()

    def __str__(self):
        return self.username
    

class UserImages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.image}"
    
    def delete(self, *args, **kwargs):
        file_path = os.path.join(settings.MEDIA_ROOT, self.image.name)
        if os.path.exists(file_path):
            os.remove(file_path)
        super().delete(*args, **kwargs)


class Group(CodeGenerate):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='groups/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        GroupMembers.objects.create(user=self.author, group=self, is_admin=True)
        return super().save(*args, **kwargs)
    

class GroupMembers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='members_group')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group')
    is_admin = models.BooleanField(default=False)
    joined = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if GroupMembers.objects.filter(user=self.user, group=self.group).exists():
            return
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"
    

class JoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='join_request')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='join_request')
    
    ACCEPTED = 1
    REJECTED = 2

    CHOICES = (
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    )
    
    status = models.IntegerField(choices=CHOICES, null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.status == self.ACCEPTED:
            GroupMembers.objects.create(user=self.user, group=self.group, is_admin=False)
        return super().delete(*args, **kwargs)


class Message(CodeGenerate):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message')
    content = models.TextField()
    group_message = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='message')
    send_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.group_message.name}"
    

class MessageFiles(models.Model):
    file = models.FileField(upload_to='files/')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='file')

    def delete(self, *args, **kwargs):
        file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        if os.path.exists(file_path):
            os.remove(file_path)
        super().delete(*args, **kwargs)
