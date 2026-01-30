import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Company, Brand, User
import uuid

# Create company
if not Company.objects.filter(code='YG').exists():
    company = Company.objects.create(
        id=uuid.uuid4(),
        name='Yogya Group',
        code='YG',
        is_active=True
    )
    print(f'Created company: {company.name}')
else:
    company = Company.objects.get(code='YG')
    print(f'Company already exists: {company.name}')

# Create brand
if not Brand.objects.filter(code='AVRIL').exists():
    brand = Brand.objects.create(
        id=uuid.uuid4(),
        company=company,
        name='AVRIL',
        code='AVRIL',
        is_active=True
    )
    print(f'Created brand: {brand.name}')
else:
    brand = Brand.objects.get(code='AVRIL')
    print(f'Brand already exists: {brand.name}')

# Create superuser with Global Level access
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@yogya.com',
        company=None,  # Global admin - no company restriction
        brand=None,    # Global admin - no brand restriction
        role='admin',
        role_scope='global'  # Global Level - can access all companies
    )
    print(f'Created superuser: {user.username} (Global Level)')
else:
    # Update existing admin to global level if needed
    admin_user = User.objects.get(username='admin')
    if admin_user.role_scope != 'global' or admin_user.company is not None:
        admin_user.role_scope = 'global'
        admin_user.company = None
        admin_user.brand = None
        admin_user.store = None
        admin_user.save()
        print(f'Updated admin user to Global Level: {admin_user.username}')
    else:
        print('Admin user already exists (Global Level)')

print('\n✅ Setup complete!')
print('Username: admin')
print('Password: admin123')
