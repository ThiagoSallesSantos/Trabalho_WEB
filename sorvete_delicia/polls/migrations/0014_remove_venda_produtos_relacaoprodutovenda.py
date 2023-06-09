# Generated by Django 4.2 on 2023-06-25 20:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0013_venda_preco'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='venda',
            name='produtos',
        ),
        migrations.CreateModel(
            name='RelacaoProdutoVenda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qtd_produto', models.IntegerField(help_text='Quantidade do mesmo produto selecionado')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='polls.produto')),
                ('venda', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.venda')),
            ],
        ),
    ]
