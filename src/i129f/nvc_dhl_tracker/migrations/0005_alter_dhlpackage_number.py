# Generated by Django 4.2.6 on 2023-12-01 17:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nvc_dhl_tracker", "0004_alter_dhlpackage_discovered"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dhlpackage",
            name="number",
            field=models.CharField(max_length=1024, unique=True),
        ),
    ]
