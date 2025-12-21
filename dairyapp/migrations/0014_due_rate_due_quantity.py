# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairyapp', '0013_mpurchase_remarks_mproductsell_remarks'),
    ]

    operations = [
        migrations.AddField(
            model_name='due',
            name='rate',
            field=models.FloatField(blank=True, default=0, help_text='Rate per unit', null=True),
        ),
        migrations.AddField(
            model_name='due',
            name='quantity',
            field=models.FloatField(blank=True, default=0, help_text='Quantity', null=True),
        ),
    ]

