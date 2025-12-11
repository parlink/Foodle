# Generated manually to add personal_rating field using ORM

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0017_add_created_by_to_recipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='personal_rating',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
