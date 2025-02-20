from django.db import models

class User(models.Model):
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

class Token(models.Model):
    access_token = models.CharField(max_length=50)
    refresh_token = models.CharField(max_length=50)
    expires_in = models.DateTimeField()
    timestamp = models.DateTimeField()

class Artist(models.Model):
    name = models.CharField(max_length=50)
    genre = models.CharField(max_length=50)

class Song(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='songs')
