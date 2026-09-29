from django.core.management.base import BaseCommand
import os
from django.core.files import File
from main.models import GalleryImage, GalleryProject
from django.conf import settings
import cloudinary
import cloudinary.api
from cloudinary_storage.storage import MediaCloudinaryStorage
import requests

class Command(BaseCommand):
    help = 'Safely migrates local gallery images to Cloudinary matching the original database filename without suffixes.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run the migration without making any actual changes to Cloudinary or the database.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        self.stdout.write("==========================================")
        self.stdout.write(f"Starting {'DRY RUN: ' if dry_run else 'ACTUAL RUN: '}Cloudinary Image Migration")
        self.stdout.write("==========================================")

        records = list(GalleryImage.objects.all())
        projects = list(GalleryProject.objects.all())
        
        total_records = len(records) * 2 + len(projects) # image + thumbnail
        
        items_to_process = []
        for img in records:
            if img.image and not str(img.image.name).startswith('http'):
                items_to_process.append((img, 'image', img.image.name))
            if img.thumbnail and not str(img.thumbnail.name).startswith('http'):
                items_to_process.append((img, 'thumbnail', img.thumbnail.name))
                
        for proj in projects:
            if proj.cover_image and not str(proj.cover_image.name).startswith('http'):
                items_to_process.append((proj, 'cover_image', proj.cover_image.name))

        local_found = 0
        local_missing = 0
        cloudinary_already_exists = 0
        requires_upload = 0
        conflicts = 0
        unmigratable = 0
        
        storage = MediaCloudinaryStorage()
        prefix = storage._get_prefix().lstrip('/')
        
        if not dry_run:
            self.stdout.write("Processing uploads...")

        for obj, field_name, name in items_to_process:
            local_path = os.path.join(settings.MEDIA_ROOT, name)
            has_local = os.path.exists(local_path)
            
            if has_local:
                local_found += 1
            else:
                local_missing += 1
                unmigratable += 1
                if not dry_run:
                    self.stdout.write(self.style.WARNING(f"SKIP: Missing local file for {name}"))
                continue

            # The expected url based on existing DB name (which could contain .jpeg) 
            # Note: storage.url() prepends media/ depending on settings
            expected_url = storage.url(name)
            head = requests.head(expected_url)
            exists_in_cloud = (head.status_code == 200)

            if exists_in_cloud:
                cloudinary_already_exists += 1
                if not dry_run:
                    self.stdout.write(self.style.SUCCESS(f"SKIP: Already exists in Cloudinary {name}"))
            else:
                requires_upload += 1
                
                if not dry_run:
                    self.stdout.write(f"Uploadiing {name}...")
                    try:
                        # Extract extension and folder to construct expected public ID natively
                        # e.g. name = gallery/images/2026/09/photo.jpeg
                        # public_id = media/gallery/images/2026/09/photo
                        
                        relative_folder = os.path.dirname(name)
                        file_fullname = os.path.basename(name)
                        file_base = os.path.splitext(file_fullname)[0]
                        
                        cloudinary_folder = os.path.join(prefix, relative_folder) if relative_folder else prefix
                        cloudinary_folder = cloudinary_folder.rstrip('/')
                        target_public_id = f"{cloudinary_folder}/{file_base}"
                        
                        with open(local_path, 'rb') as f:
                            resp = cloudinary.uploader.upload(
                                f, 
                                public_id=target_public_id,
                                use_filename=True,
                                unique_filename=False,
                                overwrite=False
                            )
                        self.stdout.write(self.style.SUCCESS(f"Uploaded {name} -> {resp.get('public_id')}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed to upload {name}: {e}"))
        
        self.stdout.write("\n==========================================")
        self.stdout.write("SUMMARY REPORT")
        self.stdout.write("==========================================")
        self.stdout.write(f"Total potential fields          : {total_records}")
        self.stdout.write(f"Items processed                 : {len(items_to_process)}")
        self.stdout.write(f"Local files found               : {local_found}")
        self.stdout.write(f"Local files missing             : {local_missing}")
        self.stdout.write(f"Cloudinary assets already exist : {cloudinary_already_exists}")
        self.stdout.write(f"Assets required to upload       : {requires_upload}")
        self.stdout.write(f"Unmigratable (missing local)    : {unmigratable}")
        self.stdout.write(f"Conflicts / Skipped             : {conflicts}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\nThis was a DRY-RUN. No changes were made."))
