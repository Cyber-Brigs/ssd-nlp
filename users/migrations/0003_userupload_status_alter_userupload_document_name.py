# Generated by Django 4.2.2 on 2024-05-21 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_email_alter_customuser_first_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userupload',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('unavailable', 'Unavailable')], default='available', max_length=12),
        ),
        migrations.AlterField(
            model_name='userupload',
            name='document_name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
