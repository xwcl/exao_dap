from django.core.management.base import BaseCommand, CommandError
from exao_dap.registrar.models import Dataset, Datum
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .... import cyverse

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        User = get_user_model()
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            is_staff=True,
            is_superuser=True
        )
        admin_user.set_password("admin")
        admin_user.save()

        user1, _ = User.objects.get_or_create(username="user1")
        user1.set_password("user1")
        user1.save()

        prefab_ds = 'admin_mini_dataset'
        ds1, _ = Dataset.objects.get_or_create(
            identifier=prefab_ds,
            friendly_name='Dataset #1',
            description='Mini dataset owned by admin but made public',
            source=Dataset.DatasetSource.ONSKY,
            stage=Dataset.DatasetStage.RAW,
            owner=admin_user,
            public=True,
            state=Dataset.DatasetState.COMPLETE
        )
        ds1.save()
        self.stdout.write(f'Created {prefab_ds} in db')
        fs = cyverse.irods_get_fs()
        files = fs.ls(f'{cyverse.IRODS_HOME}/registrar/{prefab_ds}')
        for info in files:
            if info['type'] == 'directory':
                continue
            d, _ = Datum.objects.get_or_create(
                dataset=ds1,
                filename=info['name'],
                checksum=info['checksum'],
                size_bytes=info['size'],
                kind=Datum.DatumKind.SCIENCE,
            )
            d.save()
            self.stdout.write(f'added {info["name"]} {prefab_ds}')



        ds2, _ = Dataset.objects.get_or_create(
            identifier='ds2',
            friendly_name='Dataset #2',
            description='Example dataset number two is owned by admin and not shared',
            source=Dataset.DatasetSource.ONSKY,
            stage=Dataset.DatasetStage.CALIBRATED,
            owner=admin_user,
            public=False,
            state=Dataset.DatasetState.COMPLETE
        )
        ds2.save()


        ds3, _ = Dataset.objects.get_or_create(
            identifier='ds3',
            friendly_name='Dataset #3',
            description='Example dataset number three is owned by user1, pending, and not shared',
            source=Dataset.DatasetSource.ONSKY,
            stage=Dataset.DatasetStage.REDUCED,
            owner=user1,
            public=False,
            state=Dataset.DatasetState.PENDING
        )
        ds3.save()


        ds4, _ = Dataset.objects.get_or_create(
            identifier='ds4',
            friendly_name='Dataset #4',
            description='Example dataset number four is owned by admin and shared only with user1',
            source=Dataset.DatasetSource.ONSKY,
            stage=Dataset.DatasetStage.REDUCED,
            owner=admin_user,
            public=False,
            state=Dataset.DatasetState.COMPLETE,
        )
        ds4.save()
        ds4.shared.add(user1)
