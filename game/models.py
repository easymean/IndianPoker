from django.db import models


class User(models.Model):
    nickname = models.CharField(max_length=50)
    ready_state = models.IntegerField(default=0)
    score = models.IntegerField(default=10)

    def __str__(self):
        return self.nickname


class Room(models.Model):
    name = models.CharField(max_length=500)
    group_name = models.SlugField(unique=True)
    state = models.IntegerField(default=0) # 0 한명만 있음 1 두 명이 있음 2 게임 시작
    round = models.IntegerField(default=0)
    owner = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name