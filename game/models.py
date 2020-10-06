from django.db import models


class User(models.Model):
    nickname = models.CharField(max_length=50)
    ready_state = models.IntegerField(default=0)
    score = models.IntegerField(default=10)

    def __str__(self):
        return self.nickname



class Room(models.Model):
    id = models.UUIDField(primary_key=True, default= uuid.uuid4(), editable=False)
    name = models.CharField(max_length=500)
    group_name = models.SlugField(unique=True)
    state = models.IntegerField(default=0) # 0 한명만 있음 1 두 명이 있음 2 게임 시작
    round = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)

    def make_room(self):
        hash_name = str(self.id)
        key_value = {
            "type": "room",
            "name": self.name,
            "state": self.state,
            "round": self.round,
        }
        r.hmset(hash_name, key_value);
        r.rpush("room", hash_name);

