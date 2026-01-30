# Generated manually to rename Table model to Tables
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_add_company_to_tablearea'),
    ]

    operations = [
        # Rename the model from Table to Tables
        migrations.RenameModel(
            old_name='Table',
            new_name='Tables',
        ),
        # Rename the database table from 'table' to 'tables' to avoid SQL keyword conflict
        migrations.AlterModelTable(
            name='Tables',
            table='tables',
        ),
    ]
