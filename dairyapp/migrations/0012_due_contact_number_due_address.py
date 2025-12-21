# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairyapp', '0011_buyer_alter_seller_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='due',
            name='contact_number',
            field=models.CharField(blank=True, help_text='Contact phone number', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='due',
            name='address',
            field=models.CharField(blank=True, help_text='Address of the person', max_length=200, null=True),
        ),
    ]

