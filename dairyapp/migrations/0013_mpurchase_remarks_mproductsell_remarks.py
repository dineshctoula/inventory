# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairyapp', '0012_due_contact_number_due_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='mpurchase',
            name='remarks',
            field=models.TextField(blank=True, help_text='Additional remarks or notes', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='mproductsell',
            name='remarks',
            field=models.TextField(blank=True, help_text='Additional remarks or notes', max_length=500, null=True),
        ),
    ]

