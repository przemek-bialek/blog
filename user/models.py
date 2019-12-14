from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    img = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username}\'s profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.img.path)

        if img.width > 250:
            if img.height > 250:
                img.thumbnail((250, 250))
            else:
                img.thumbnail((250, img.height))
        else:
            if img.height > 250:
                img.thumbnail((img.height, 250))
        img.save(self.img.path)
