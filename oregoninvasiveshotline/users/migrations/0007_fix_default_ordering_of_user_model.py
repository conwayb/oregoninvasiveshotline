from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20151013_1331'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['first_name', 'last_name']},
        ),
    ]
