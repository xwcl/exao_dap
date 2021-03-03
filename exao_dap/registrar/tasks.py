import os.path
from .serializers import DatumSerializer
from .models import Datum
from .. import cyverse
from exao_dap_client import datum

def populate_metadata(datum_pk):
    the_datum = Datum.objects.get(pk=datum_pk)
    if the_datum.state is Datum.DatumState.SYNCED:
        return
    dest_path = the_datum.data_store_path()
    source_path = os.path.join(the_datum.dataset.source_path, the_datum.filename)
    irodsfs = cyverse.irods_get_fs()
    if not irodsfs.exists(dest_path):
        irodsfs.cp_file(source_path, dest_path)

    with irodsfs.open(dest_path) as fh:
        the_datum.state = Datum.DatumState.SYNCING
        the_datum.save()

        payload = datum.make_payload(the_datum.filename, file_like=fh)

    ser = DatumSerializer(instance=the_datum, data=payload, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save(state=Datum.DatumState.SYNCED)

