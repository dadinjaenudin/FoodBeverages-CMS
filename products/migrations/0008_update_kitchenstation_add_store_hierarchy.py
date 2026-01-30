# Generated migration for KitchenStation hierarchy update

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_add_store_to_tablearea'),
        ('products', '0007_add_store_to_tablearea'),
    ]

    operations = [
        # Add new fields
        migrations.AddField(
            model_name='kitchenstation',
            name='store',
            field=models.ForeignKey(blank=True, help_text='Store-specific stations (leave blank for brand-wide)', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='kitchen_stations', to='core.store'),
        ),
        migrations.AddField(
            model_name='kitchenstation',
            name='description',
            field=models.TextField(blank=True, help_text='Description of the kitchen station'),
        ),
        migrations.AddField(
            model_name='kitchenstation',
            name='sort_order',
            field=models.IntegerField(default=0, help_text='Display order'),
        ),
        
        # Remove old unique constraint
        migrations.AlterUniqueTogether(
            name='kitchenstation',
            unique_together=set(),
        ),
        
        # Update meta ordering
        migrations.AlterModelOptions(
            name='kitchenstation',
            options={'ordering': ['brand', 'store', 'sort_order', 'name'], 'verbose_name': 'Kitchen Station', 'verbose_name_plural': 'Kitchen Stations'},
        ),
        
        # Add new unique constraint
        migrations.AlterUniqueTogether(
            name='kitchenstation',
            unique_together={('brand', 'store', 'code')},
        ),
        
        # Add new indexes
        migrations.AddIndex(
            model_name='kitchenstation',
            index=models.Index(fields=['store', 'is_active'], name='kitchen_sta_store_i_173560_idx'),
        ),
    ]