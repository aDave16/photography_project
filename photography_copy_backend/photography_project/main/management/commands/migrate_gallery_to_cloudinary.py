from django.core.management.base import BaseCommand
import os
from main.models import GalleryImage, GalleryProject
from django.conf import settings
import cloudinary
import cloudinary.api
import cloudinary.uploader
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
        
        items_to_process = []
        for img in records:
            if img.image and not str(img.image.name).startswith('http'):
                items_to_process.append((img, 'GalleryImage.image', img.image.name))
            if img.thumbnail and not str(img.thumbnail.name).startswith('http'):
                items_to_process.append((img, 'GalleryImage.thumbnail', img.thumbnail.name))
                
        for proj in projects:
            if proj.cover_image and not str(proj.cover_image.name).startswith('http'):
                items_to_process.append((proj, 'GalleryProject.cover_image', proj.cover_image.name))

        stats = {
            'total_records': len(items_to_process),
            'already_exists': 0,
            'needs_upload': 0,
            'local_missing': 0,
            'suffixed_found': 0,
            'conflicts': 0,
            'errors': 0
        }
        
        storage = MediaCloudinaryStorage()
        prefix = storage._get_prefix().lstrip('/')
        
        if not dry_run:
            self.stdout.write("Processing uploads...")

        for obj, field_name, name in items_to_process:
            self.stdout.write(f"\nProcessing [{field_name}]: {name}")
            local_path = os.path.join(settings.MEDIA_ROOT, name)
            has_local = os.path.exists(local_path)
            
            if not has_local:
                stats['local_missing'] += 1
                self.stdout.write(self.style.WARNING(f"  -> MISSING LOCAL FILE: {local_path}"))
                continue

            # Determine desired Cloudinary public_id
            relative_folder = os.path.dirname(name)
            file_fullname = os.path.basename(name)
            file_base = os.path.splitext(file_fullname)[0]
            
            cloudinary_folder = os.path.join(prefix, relative_folder) if relative_folder else prefix
            cloudinary_folder = cloudinary_folder.rstrip('/')
            
            target_public_id = f"{cloudinary_folder}/{file_base}"
            if target_public_id.startswith('/'):
                target_public_id = target_public_id[1:]
                
            self.stdout.write(f"  -> Target public_id: {target_public_id}")

            # Check exact suffix-free existence via API
            exists_exactly = False
            try:
                cloudinary.api.resource(target_public_id)
                exists_exactly = True
            except cloudinary.exceptions.NotFound:
                exists_exactly = False
            except Exception as e:
                stats['errors'] += 1
                self.stdout.write(self.style.ERROR(f"  -> API Error checking exact resource: {e}"))
                continue

            # Check if suffixed versions exist
            has_suffixed = False
            try:
                res = cloudinary.api.resources(type='upload', prefix=target_public_id)
                resources = res.get('resources', [])
                for r in resources:
                    if r.get('public_id') != target_public_id and r.get('public_id').startswith(target_public_id + "_"):
                        has_suffixed = True
                        break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  -> API Error checking for suffixes: {e}"))

            if has_suffixed:
                stats['suffixed_found'] += 1
                self.stdout.write(self.style.WARNING(f"  -> SUFFIXED OLD ASSETS FOUND starting with {target_public_id}_"))

            if exists_exactly:
                stats['already_exists'] += 1
                self.stdout.write(self.style.SUCCESS(f"  -> ALREADY EXISTS. Skipping upload."))
                continue
            else:
                stats['needs_upload'] += 1
                self.stdout.write(self.style.WARNING(f"  -> NEEDS UPLOAD."))
                
                if not dry_run:
                    self.stdout.write(f"  -> Uploading explicitly as {target_public_id}...")
                    try:
                        with open(local_path, 'rb') as f:
                            resp = cloudinary.uploader.upload(
                                f, 
                                public_id=target_public_id,
                                overwrite=False
                            )
                        self.stdout.write(self.style.SUCCESS(f"  -> Successfully uploaded: {resp.get('public_id')}"))
                    except Exception as e:
                        stats['errors'] += 1
                        self.stdout.write(self.style.ERROR(f"  -> Failed to upload {name}: {e}"))
        
        self.stdout.write("\n==========================================")
        self.stdout.write("SUMMARY REPORT")
        self.stdout.write("==========================================")
        self.stdout.write(f"TOTAL RECORDS             : {stats['total_records']}")
        self.stdout.write(f"ALREADY EXISTS            : {stats['already_exists']}")
        self.stdout.write(f"NEEDS UPLOAD              : {stats['needs_upload']}")
        self.stdout.write(f"LOCAL FILE MISSING        : {stats['local_missing']}")
        self.stdout.write(f"SUFFIXED OLD ASSETS FOUND : {stats['suffixed_found']}")
        self.stdout.write(f"CONFLICTS                 : {stats['conflicts']}")
        self.stdout.write(f"ERRORS                    : {stats['errors']}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\nThis was a DRY-RUN. No changes were made."))
        else:
            self.stdout.write(self.style.SUCCESS("\nMigration completed successfully."))
