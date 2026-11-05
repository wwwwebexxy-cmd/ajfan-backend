from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="customer",
            old_name="zip_address",
            new_name="swift_address",
        ),
        migrations.RenameField(
            model_name="customer",
            old_name="ifsc",
            new_name="trn",
        ),
        migrations.AlterField(
            model_name="customer",
            name="swift_address",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
