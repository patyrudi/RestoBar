# Generated by Django 5.1 on 2024-12-03 23:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurante_api', '0006_remove_area_empleado_empleado_area_alter_mesa_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumo',
            name='empleado',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='consumos', to='restaurante_api.empleado'),
        ),
    ]
