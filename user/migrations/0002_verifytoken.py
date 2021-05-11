# Generated by Django 3.2.1 on 2021-05-05 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerifyToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, null=True)),
                ('tokens', models.TextField(null=True)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('is_used', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'verify_token',
            },
        ),
    ]
