# Generated by Django 4.2 on 2023-06-04 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0006_sorvete_descricao_alter_produto_componenetes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sorvete',
            name='ingredientes',
            field=models.ManyToManyField(to='polls.ingrediente'),
        ),
    ]
