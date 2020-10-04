# Generated by Django 3.0 on 2020-10-04 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('year', '0001_initial'),
        ('committee', '0004_remove_committee_candidacies'),
    ]

    operations = [
        migrations.AddField(
            model_name='committee',
            name='years',
            field=models.ManyToManyField(related_name='committee_relations', to='year.Year'),
        ),
    ]