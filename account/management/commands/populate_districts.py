from django.core.management.base import BaseCommand
from account.models import District  # Replace 'your_app' with your actual app name


class Command(BaseCommand):
    help = "Populates the District model with Sierra Leone districts"

    def handle(self, *args, **kwargs):
        districts_data = [
            {'name': 'Kailahun', 'region': 'Eastern', 'description': 'Known for agriculture.', 'population': 525000,
             'literacy_rate': 48.0, 'land_area_km2': 3860},
            {'name': 'Kenema', 'region': 'Eastern', 'description': 'A major commercial hub.', 'population': 609000,
             'literacy_rate': 50.2, 'land_area_km2': 6563},
            {'name': 'Kono', 'region': 'Eastern', 'description': 'Famous for diamond mining.', 'population': 505000,
             'literacy_rate': 46.3, 'land_area_km2': 5474},
            {'name': 'Bombali', 'region': 'Northern', 'description': 'Hosts the city of Makeni.', 'population': 606000,
             'literacy_rate': 54.0, 'land_area_km2': 7519},
            {'name': 'Kambia', 'region': 'Northern', 'description': 'Border district with Guinea.',
             'population': 343000, 'literacy_rate': 45.6, 'land_area_km2': 3118},
            {'name': 'Port Loko', 'region': 'Northern', 'description': 'Major trading district.', 'population': 615000,
             'literacy_rate': 47.8, 'land_area_km2': 5718},
            {'name': 'Tonkolili', 'region': 'Northern', 'description': 'Known for iron ore mining.',
             'population': 530000, 'literacy_rate': 48.1, 'land_area_km2': 7205},
            {'name': 'Bo', 'region': 'Southern', 'description': 'Second largest city in Sierra Leone.',
             'population': 575000, 'literacy_rate': 51.4, 'land_area_km2': 5022},
            {'name': 'Bonthe', 'region': 'Southern', 'description': 'Island district.', 'population': 220000,
             'literacy_rate': 40.0, 'land_area_km2': 3246},
            {'name': 'Moyamba', 'region': 'Southern', 'description': 'A historical district.', 'population': 318000,
             'literacy_rate': 43.2, 'land_area_km2': 6902},
            {'name': 'Pujehun', 'region': 'Southern', 'description': 'Known for coastal resources.',
             'population': 345000, 'literacy_rate': 41.8, 'land_area_km2': 4561},
            {'name': 'Western Area Urban', 'region': 'Western', 'description': 'Freetown, the capital city.',
             'population': 1145000, 'literacy_rate': 70.0, 'land_area_km2': 557},
            {'name': 'Western Area Rural', 'region': 'Western', 'description': 'Surrounding Freetown.',
             'population': 444000, 'literacy_rate': 60.2, 'land_area_km2': 483},
        ]

        for district_data in districts_data:
            district, created = District.objects.get_or_create(
                name=district_data['name'],
                defaults={
                    'region': district_data['region'],
                    'description': district_data['description'],
                    'population': district_data.get('population'),
                    'literacy_rate': district_data.get('literacy_rate'),
                    'land_area_km2': district_data.get('land_area_km2'),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully added district: {district.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"District already exists: {district.name}"))
