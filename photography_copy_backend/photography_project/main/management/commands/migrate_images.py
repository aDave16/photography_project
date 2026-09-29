import os
from django.core.management.base import BaseCommand
from django.core.files import File
from main.models import GalleryImage, GalleryProject
from photography_project import settings

class Command(BaseCommand):
    help = 'Safely migrates local gallery images to Cloudinary without deleting the local files.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting migration of local images to Cloudinary...")

        # MIGRATING GALLERY IMAGES
        images = GalleryImage.objects.all()
        for img in images:
            if img.image and not img.image.name.startswith('http'):
                self.stdout.write(f"Migrating GalleryImage #{img.id}: {img.image.name}")
                local_path = os.path.join(settings.MEDIA_ROOT, img.image.name)
                
                if os.path.exists(local_path):
                    with open(local_path, 'rb') as f:
                        # This will upload it to Cloudinary utilizing the backend
                        img.image.save(img.image.name, File(f), save=True)
                    self.stdout.write(self.style.SUCCESS(f"Successfully migrated GalleryImage #{img.id}"))
                else:
                    self.stdout.write(self.style.WARNING(f"File not found locally for GalleryImage #{img.id}: {local_path}"))
            
            if img.thumbnail and not img.thumbnail.name.startswith('http'):
                 local_path = os.path.join(settings.MEDIA_ROOT, img.thumbnail.name)
                 if os.path.exists(local_path):
                     with open(local_path, 'rb') as f:
                         img.thumbnail.save(img.thumbnail.name, File(f), save=True)
                     self.stdout.write(self.style.SUCCESS(f"Successfully migrated thumbnail for GalleryImage #{img.id}"))

        # MIGRATING GALLERY PROJECTS
        projects = GalleryProject.objects.all()
        for proj in projects:
            if proj.cover_image and not proj.cover_image.name.startswith('http'):
                self.stdout.write(f"Migrating GalleryProject Cover #{proj.id}: {proj.cover_image.name}")
                local_path = os.path.join(settings.MEDIA_ROOT, proj.cover_image.name)
                
                if os.path.exists(local_path):
                    with open(local_path, 'rb') as f:
                        proj.cover_image.save(proj.cover_image.name, File(f), save=True)
                    self.stdout.write(self.style.SUCCESS(f"Successfully migrated GalleryProject Cover #{proj.id}"))
                else:
                     self.stdout.write(self.style.WARNING(f"File not found locally for GalleryProject #{proj.id}: {local_path}"))

        self.stdout.write(self.style.SUCCESS('Migration complete! Please verify Cloudinary before deleting any local media files.'))
