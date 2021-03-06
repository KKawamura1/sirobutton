# Generated by Django 2.0.6 on 2018-06-25 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0005_video_published'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='tag title')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='tag created time')),
            ],
        ),
        migrations.AddField(
            model_name='subtitle',
            name='tags',
            field=models.ManyToManyField(to='hello.Tag'),
        ),
    ]
