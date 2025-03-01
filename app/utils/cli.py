import click
from flask.cli import with_appcontext
from app import db
from app.models import User, Department, Doctor
from faker import Faker

fake = Faker()

def register_commands(app):
    """CLI commands"""
    
    @app.cli.command('create-admin')
    @click.option('--email', default='admin@hospital.com')
    @click.option('--password', default='admin123')
    @with_appcontext
    def create_admin(email, password):
        """Create admin user"""
        user = User(
            email=email,
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        click.echo(f'Admin user created: {email}')
    
    @app.cli.command('create-departments')
    @with_appcontext
    def create_departments():
        """Create default departments"""
        departments = [
            ('Cardiology', 'Heart and vascular diseases'),
            ('Neurology', 'Nervous system diseases'),
            ('Orthopedics', 'Musculoskeletal system diseases'),
            ('Ophthalmology', 'Eye and vision related diseases'),
            ('ENT', 'Ear, Nose, and Throat diseases'),
            ('Internal Medicine', 'Internal diseases'),
            ('Pediatrics', 'Child health and diseases'),
            ('Gynecology', 'Women\'s health'),
            ('Urology', 'Urological diseases'),
            ('Psychiatry', 'Mental health and diseases')
        ]
        
        for name, description in departments:
            department = Department(
                name=name,
                description=description
            )
            db.session.add(department)
        
        db.session.commit()
        click.echo('Default departments created')
    
    @app.cli.command('create-test-data')
    @with_appcontext
    def create_test_data():
        """Create test users"""
        # Create test patients
        for _ in range(10):
            user = User(
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='patient',
                phone=fake.phone_number(),
                address=fake.address()
            )
            user.set_password('password123')
            db.session.add(user)
        
        # Create test doctors
        departments = Department.query.all()
        for department in departments:
            for _ in range(2):
                user = User(
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role='doctor',
                    phone=fake.phone_number()
                )
                user.set_password('password123')
                db.session.add(user)
                db.session.flush()
                
                doctor = Doctor(
                    user_id=user.id,
                    department_id=department.id,
                    specialization=fake.job(),
                    qualification=fake.text(max_nb_chars=200),
                    experience_years=fake.random_int(min=1, max=30),
                    license_number=fake.unique.random_number(digits=8),
                    consultation_fee=fake.random_int(min=100, max=500),
                    bio=fake.text()
                )
                db.session.add(doctor)
        
        db.session.commit()
        click.echo('Test users created')
    
    @app.cli.command('init-db')
    @with_appcontext
    def init_db():
        """Reset and recreate the database"""
        try:
            db.drop_all()
            db.create_all()
            click.echo('Database reset successfully')
            
            # Create default data
            create_departments()
            create_admin(email='admin@hospital.com', password='admin123')
            create_test_data()
            
            click.echo('Default data created')
            
        except Exception as e:
            click.echo(f'Error: {str(e)}')
    
    @app.cli.command('backup-db')
    @click.argument('filename')
    @with_appcontext
    def backup_db(filename):
        """Backup the database"""
        import subprocess
        import os
        from datetime import datetime
        
        try:
            # Timestamp for backup file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{filename}_{timestamp}.sql"
            
            # PostgreSQL backup command
            command = f"pg_dump -U {app.config['DB_USER']} -h {app.config['DB_HOST']} "
            command += f"-p {app.config['DB_PORT']} {app.config['DB_NAME']} > {backup_file}"
            
            subprocess.run(command, shell=True, check=True)
            click.echo(f'Database backup completed: {backup_file}')
            
        except Exception as e:
            click.echo(f'Backup error: {str(e)}')

def init_app(app):
    app.cli.add_command(create_admin)
    app.cli.add_command(create_departments)
    app.cli.add_command(create_test_data) 