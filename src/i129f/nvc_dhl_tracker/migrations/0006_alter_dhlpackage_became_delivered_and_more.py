# Generated by Django 4.2.6 on 2023-12-01 18:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nvc_dhl_tracker", "0005_alter_dhlpackage_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dhlpackage",
            name="became_delivered",
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name="dhlpackage",
            name="became_pre_transit",
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name="dhlpackage",
            name="became_transit",
            field=models.DateTimeField(null=True),
        ),
    ]
