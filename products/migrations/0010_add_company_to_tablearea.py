# Generated manually for TableArea.company field addition

from django.db import migrations, models
import django.db.models.deletion


def populate_company_from_brand(apps, schema_editor):
    """Populate company field from brand relationship"""
    TableArea = apps.get_model('products', 'TableArea')
    for area in TableArea.objects.all():
        if area.brand_id:
            area.company_id = area.brand.company_id
            area.save(update_fields=['company_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_rename_kitchen_sta_store_i_173560_idx_kitchen_sta_store_i_4d6c03_idx'),
        ('core', '0008_add_store_to_tablearea'),
    ]

    operations = [
        migrations.AddField(
            model_name='tablearea',
            name='company',
            field=models.ForeignKey(
                blank=True,
                help_text='Company for multi-tenant isolation',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='table_areas',
                to='core.company'
            ),
        ),
        migrations.RunPython(populate_company_from_brand, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='tablearea',
            name='company',
            field=models.ForeignKey(
                blank=True,
                help_text='Company for multi-tenant isolation',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='table_areas',
                to='core.company'
            ),
        ),
        migrations.AlterModelOptions(
            name='tablearea',
            options={
                'ordering': ['company', 'brand', 'store', 'sort_order', 'name'],
                'verbose_name': 'Table Area',
                'verbose_name_plural': 'Table Areas'
            },
        ),
        migrations.AddIndex(
            model_name='tablearea',
            index=models.Index(fields=['company', 'is_active'], name='table_area_company_active_idx'),
        ),
    ]
