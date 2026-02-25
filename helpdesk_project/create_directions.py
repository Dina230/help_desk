# create_directions.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk_project.settings')
django.setup()

from helpdesk.models import Direction

directions = [
    ('OS', 'Операционная система'),
    ('ZUP', '1с ЗиУП'),
    ('PU', '1с ПУ'),
    ('BU', '1с БУ'),
    ('TEL', 'Телефония'),
    ('VIDEO_PKS', 'Видеонаблюдение на ПКС'),
    ('VIDEO_PC', 'Видеонаблюдение общие проблемы с ПК'),
]

for code, name in directions:
    direction, created = Direction.objects.get_or_create(
        name=code,
        defaults={'display_name': name}
    )
    if created:
        print(f'Создано направление: {name}')
    else:
        print(f'Направление уже существует: {name}')

print('Готово!')