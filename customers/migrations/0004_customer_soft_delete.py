from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0003_customer_iban"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="customer",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
