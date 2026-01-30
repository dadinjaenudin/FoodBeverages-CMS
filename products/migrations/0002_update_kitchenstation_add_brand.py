# Generated manually

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        # Drop old kitchen_station table with CASCADE
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS kitchen_station CASCADE;',
            reverse_sql='SELECT 1;'
        ),
        
        # Recreate with brand field
        migrations.CreateModel(
            name='KitchenStation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('code', models.CharField(max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='kitchen_stations', to='core.brand')),
            ],
            options={
                'verbose_name': 'Kitchen Station',
                'verbose_name_plural': 'Kitchen Stations',
                'db_table': 'kitchen_station',
                'ordering': ['name'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='kitchenstation',
            unique_together={('brand', 'code')},
        ),
        migrations.AddIndex(
            model_name='kitchenstation',
            index=models.Index(fields=['brand', 'is_active'], name='kitchen_sta_brand_i_0d8a44_idx'),
        ),
        migrations.AddIndex(
            model_name='kitchenstation',
            index=models.Index(fields=['code'], name='kitchen_sta_code_722d93_idx'),
        ),
    ]
