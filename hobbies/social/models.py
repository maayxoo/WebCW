from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Profile(models.Model):

    text = models.CharField(max_length=4096)
    image = models.ImageField(upload_to='profile_images')

    def __str__(self):
        return f"{self.text} ({self.member_check})"

    def to_dict(self):
        return {
            'text': self.text,
            'image': self.image.url if self.image else None,
        }

    @property
    def has_member(self):
        
        return hasattr(self, 'member') and self.member is not None

    @property
    def member_check(self):

        return str(self.member) if self.has_member else 'NONE'


class User(AbstractUser):

    username = models.CharField(max_length=50, unique=True)
    profile = models.OneToOneField(
        to=Profile,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    following = models.ManyToManyField(
        to='self',
        blank=True,
        symmetrical=False,
        related_name='followers',
    )
    messages = models.ManyToManyField(
        to='self',
        blank=True,
        symmetrical=False,
        through='Message',
        related_name='related_to'
    )

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def to_dict(self):
        return {
            'username': self.username,
            'profile': self.profile.to_dict() if self.profile else None,
            'messages': [ message.to_dict() for message in self.messages ]
        }

    @property
    def messages(self):

        return (self.sent.all() | self.received.all()).order_by("-time")

    def messages_with(self, view_user):

        m1 = Message.objects.filter(recip=view_user, public=True)
        m2 = Message.objects.filter(sender=view_user, public=True)
        m3 = Message.objects.filter(sender=self, recip=view_user)
        m4 = Message.objects.filter(sender=view_user, recip=self)
        return m1.union(m2, m3, m4).order_by('-time')

    @property
    def following_count(self):

        return self.following.count()

    @property
    def follower_count(self):
        
        return User.objects.filter(following__id=self.id).count()


class Message(models.Model):

    sender = models.ForeignKey(
        to=User,
        related_name='sent',
        on_delete=models.CASCADE
    )
    recip = models.ForeignKey(
        to=User,
        related_name='received',
        on_delete=models.CASCADE
    )
    text = models.CharField(max_length=4096)
    public = models.BooleanField(default=True)
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"From {self.sender} to {self.recip}"

    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender.username,
            'recip': self.recip.username,
            'text': self.text,
            'public': self.public,
            'time': str(self.time)[:16], # self.time.strftime("%d/%m/%y"),
        }

class Hobbies(models.Model):
    hobby_name = models.CharField(max_length=30)

    def __str__(self):
        return self.hobby_name

    def to_dict(self):
        return {
            'name': self.hobby_name
        }