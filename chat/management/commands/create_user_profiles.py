from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from chat.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile objects for all existing users who do not have profiles'

    def handle(self, *args, **options):
        users_without_profiles = []
        profiles_created = 0
        
        for user in User.objects.all():
            try:
                # Try to access the profile
                user.profile
            except UserProfile.DoesNotExist:
                # Profile doesn't exist, create it
                UserProfile.objects.create(user=user)
                users_without_profiles.append(user.username)
                profiles_created += 1
        
        if profiles_created > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {profiles_created} user profile(s) for: {", ".join(users_without_profiles)}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All users already have profiles!')
            ) 