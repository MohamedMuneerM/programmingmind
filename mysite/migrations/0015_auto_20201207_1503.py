# Generated by Django 3.1.3 on 2020-12-07 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0014_auto_20201207_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorial',
            name='content',
            field=models.TextField(),
        ),
    ]
