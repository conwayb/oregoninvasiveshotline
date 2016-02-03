from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0006_auto_20151013_1331'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='report',
            options={'ordering': ['-created_on']},
        ),
    ]
