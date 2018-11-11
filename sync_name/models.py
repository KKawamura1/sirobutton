from django.db import models


class TwitterAccount(models.Model):
    id = models.AutoField(primary_key=True)
    twitter_id = models.CharField('Twitter id', max_length=30)
    oauth_token = models.CharField('OAuth Token', max_length=50)
    oauth_secret = models.CharField('OAuth Secret Token', max_length=50)
    last_prefix = models.CharField('Prefix of the name since last updated', max_length=50)
    last_updated = models.DateTimeField('Last modified time', auto_now=True)

    def __str__(self) -> str:
        return f'<TwitterAccount of id: {self.twitter_id}>'
