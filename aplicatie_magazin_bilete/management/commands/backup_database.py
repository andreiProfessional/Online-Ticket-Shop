from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection
from datetime import datetime
import os


class Command(BaseCommand):
    help = 'Creează un backup al bazei de date prin generarea comenzilor INSERT pentru toate tabelele'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Calea către fișierul de backup (opțional, implicit: backup_TIMESTAMP.sql)',
        )

    def handle(self, *args, **options):
        # Generează numele fișierului de backup
        if options['output']:
            output_file = options['output']
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'backup_{timestamp}.sql'

        # Obține modelele din aplicație
        app_config = apps.get_app_config('aplicatie_magazin_bilete')
        models_to_backup = app_config.get_models()

        # Deschide fișierul pentru scriere
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"-- Backup bază de date generat la: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Database: {connection.settings_dict['NAME']}\n")
            f.write("-- ATENȚIE: Executați acest script într-o bază de date goală!\n\n")
            f.write("SET CLIENT_ENCODING TO 'UTF8';\n")
            f.write("SET STANDARD_CONFORMING_STRINGS TO ON;\n\n")

            # Procesează fiecare model
            for model in models_to_backup:
                # Ignoră modelul Accesare care nu este un model Django real
                if model.__name__ == 'Accesare':
                    continue

                table_name = model._meta.db_table
                objects = model.objects.all()
                
                if objects.count() == 0:
                    f.write(f"-- Tabelul {table_name} nu conține date\n\n")
                    continue

                f.write(f"-- Date pentru tabelul: {table_name}\n")
                f.write(f"-- Model: {model.__name__}\n")
                f.write(f"-- Număr de înregistrări: {objects.count()}\n\n")

                # Obține numele coloanelor
                fields = model._meta.get_fields()
                field_names = []
                
                for field in fields:
                    # Ignoră reverse relations și many-to-many
                    if field.concrete and not field.many_to_many:
                        field_names.append(field.column)

                # Generează INSERT pentru fiecare obiect
                for obj in objects:
                    values = []
                    for field in fields:
                        if field.concrete and not field.many_to_many:
                            value = getattr(obj, field.name)
                            
                            # Formatează valoarea în funcție de tip
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, bool):
                                values.append('TRUE' if value else 'FALSE')
                            elif isinstance(value, (int, float)):
                                values.append(str(value))
                            elif isinstance(value, datetime):
                                values.append(f"'{value.isoformat()}'")
                            else:
                                # Escape single quotes pentru strings
                                escaped_value = str(value).replace("'", "''")
                                values.append(f"'{escaped_value}'")

                    # Scrie comanda INSERT
                    columns_str = ', '.join(field_names)
                    values_str = ', '.join(values)
                    f.write(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});\n")

                # Procesează relațiile many-to-many
                for field in fields:
                    if field.many_to_many and field.concrete:
                        m2m_table = field.m2m_db_table()
                        f.write(f"\n-- RelațiiMany-to-Many pentru: {field.name}\n")
                        
                        for obj in objects:
                            related_objects = getattr(obj, field.name).all()
                            for related_obj in related_objects:
                                # Obține numele coloanelor FK
                                from_column = field.m2m_column_name()
                                to_column = field.m2m_reverse_name()
                                
                                # Obține valorile PK
                                from_id = str(getattr(obj, model._meta.pk.name))
                                to_id = str(getattr(related_obj, related_obj._meta.pk.name))
                                
                                # Scrie INSERT pentru tabela intermediară
                                f.write(f"INSERT INTO {m2m_table} ({from_column}, {to_column}) VALUES ('{from_id}', '{to_id}');\n")

                f.write("\n")

            f.write("-- Backup complet!\n")

        self.stdout.write(self.style.SUCCESS(f'✓ Backup creat cu succes: {output_file}'))
        self.stdout.write(f'  Dimensiune fișier: {os.path.getsize(output_file)} bytes')
