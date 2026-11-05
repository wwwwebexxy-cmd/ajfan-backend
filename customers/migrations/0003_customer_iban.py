from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0002_rename_zip_address_customer_swift_address_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="iban",
            field=models.CharField(blank=True, max_length=34),
        ),
    ]
