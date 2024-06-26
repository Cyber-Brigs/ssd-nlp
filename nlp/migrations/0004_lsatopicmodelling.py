# Generated by Django 4.2.2 on 2024-05-11 08:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
        ('nlp', '0003_ldatopicmodelling_coherence_value_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LsaTopicModelling',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('lsa_topics_file_path', models.FileField(upload_to='topic_models/lsa/')),
                ('selected_topics', models.PositiveIntegerField(blank=True, null=True)),
                ('coherence_value', models.FloatField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('text_processing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nlp.textprocessing')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_upload', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.userupload')),
            ],
        ),
    ]
