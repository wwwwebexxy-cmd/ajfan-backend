from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("image", models.ImageField(blank=True, null=True, upload_to="services/")),
                ("service_charge", models.DecimalField(decimal_places=2, max_digits=10)),
                ("includes_government_fee", models.BooleanField(default=False)),
                ("government_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("description", models.TextField(blank=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("-created_at", "-id")},
        ),
    ]
