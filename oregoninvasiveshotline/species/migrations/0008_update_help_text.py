from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('species', '0007_auto_20160120_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='icon',
            field=models.ImageField(null=True, upload_to='icons', help_text='It is expected that the icon came from http://mapicons.mapsmarker.com/ and that it has a transparent background with a white foreground', blank=True),
        ),
        migrations.AlterField(
            model_name='severity',
            name='color',
            field=models.CharField(validators=[django.core.validators.RegexValidator('#[0-9A-Fa-f]{6}')], max_length=7, help_text='An HTML color of the form "#rrggbb"'),
        ),
    ]
