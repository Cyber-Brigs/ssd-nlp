# Generated by Django 4.2.2 on 2024-05-09 14:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextProcessing',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('start_page', models.PositiveIntegerField()),
                ('end_page', models.PositiveIntegerField()),
                ('processed_text_path', models.FileField(upload_to='processed_files/texts/')),
                ('corpus_path', models.FileField(upload_to='processed_files/corpora/')),
                ('dictionary_path', models.FileField(upload_to='processed_files/dictionaries/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_upload', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.userupload')),
            ],
        ),
        migrations.CreateModel(
            name='LdaTopicModelling',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('lda_topics_file_path', models.FileField(upload_to='topic_models/lda/')),
                ('selected_topics', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('lda_list', models.BinaryField(blank=True, null=True)),
                ('text_processing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nlp.textprocessing')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_upload', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.userupload')),
            ],
        ),
    ]
