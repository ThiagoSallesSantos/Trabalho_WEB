# Generated by Django 4.2 on 2023-06-25 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0012_delete_cupom_rename_cliente_id_venda_cliente_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='venda',
            name='preco',
            field=models.FloatField(default=True, help_text='Valor em reais'),
        ),
    ]