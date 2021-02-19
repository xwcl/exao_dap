import re
import os.path
from django.conf import settings
from django.core.exceptions import ValidationError
from django import forms
from . import models, utils
from ..cyverse import irods_check_access, irods_get_fs, IRODS_HOME

def _clean_irods_ingest_path(data):
    path = os.path.normpath(data)
    if path.startswith(IRODS_HOME):
        raise ValidationError(f"Ingest path must be outside {IRODS_HOME}")
    if not irods_check_access(path):
        raise ValidationError(f"Could not access {path} as exao_dap user")
    irodsfs = irods_get_fs()
    if len(utils.sorted_filenames(irodsfs.ls(path))) == 0:
        raise ValidationError(f"No data objects in {path} (did you want a subcollection of {path}?)")
    return path

class IngestPathVerifyForm(forms.Form):
    path = forms.CharField(max_length=models.MAX_SUPPORTED_PATH_LENGTH, label='CyVerse Data Store path')
    def clean_path(self):
        data = self.cleaned_data['path']
        return _clean_irods_ingest_path(data)


class IngestForm(IngestPathVerifyForm):
    identifier = forms.RegexField(
        regex=r'^[A-Za-z0-9_]+$',
        strip=True,
        max_length=models.MAX_IDENTIFIER_LENGTH,
        help_text='Must be unique. Use letters, numbers, and underscores.',
    )

    def clean_identifier(self):
        identifier = self.cleaned_data['identifier']
        other_dataset = models.DataSet.objects.filter(
            source_path=os.path.join(models.PATH_BASE, identifier)
        )
        if other_dataset.exists():
            raise ValidationError(f"Identifier {identifier} is already in use by a dataset")
        return identifier

    name = forms.CharField(
        max_length=models.MAX_IDENTIFIER_LENGTH,
    )
    path = forms.CharField(
        widget=forms.HiddenInput(),
        max_length=models.MAX_IDENTIFIER_LENGTH,
    )
    source = forms.ChoiceField(
        widget=forms.widgets.RadioSelect(),
        choices=models.DataSet.DataSetSource.choices
    )
    stage = forms.ChoiceField(
        widget=forms.widgets.RadioSelect(),
        choices=models.DataSet.DataSetStage.choices
    )
    description = forms.CharField(
        widget=forms.Textarea(),
        required=False
    )
    def __init__(self, *args, user=None, cleaned_irods_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is None:
            raise RuntimeError("Required argument user=")
        self.user = user
        if cleaned_irods_path is None:
            # it better be in the request data then!
            cleaned_irods_path = self.fields['path'].clean(self.data['path'])
        self.cleaned_irods_path = cleaned_irods_path
        irodsfs = irods_get_fs()
        contents = irodsfs.ls(cleaned_irods_path)

        # Add radio buttons for each file
        self.data_kind_field_names = []
        self.data_kinds = models.Datum.DatumKind.choices + [('ignore', 'ignore')]
        for filename in utils.sorted_filenames(contents):
            field = forms.ChoiceField(
                label=filename,
                widget=forms.widgets.RadioSelect(),
                choices=self.data_kinds,
                initial='ignore'
            )
            field_name = f"datum_{filename}"
            self.fields[field_name] = field
            self.data_kind_field_names.append(field_name)

    def clean(self):
        cleaned_data = super().clean()
        retained_files = 0
        for field_name in self.data_kind_field_names:
            if cleaned_data.get(field_name) != 'ignore':
                retained_files += 1
        if retained_files == 0:
            raise ValidationError("At least one file must be assigned a kind other than 'ignore' to create this dataset")

    def get_initial_for_field(self, field, field_name):
        if field_name == 'identifier':
            return re.sub(r'(/iplant/home/[^/]+/)', '', self.cleaned_irods_path).replace('/', '_')
        elif field_name == 'path':
            return self.cleaned_irods_path
        return super().get_initial_for_field(field, field_name)

    def to_serializer_payload(self):
        if self.is_valid:
            payload = {}
            for key in self.fields:
                if key in self.data_kind_field_names:
                    continue
                payload[key] = self.cleaned_data[key]
            payload['datum_set'] = []
            for key in self.data_kind_field_names:
                field = self.fields[key]
                datum = {
                    'filename': field.label,
                    'kind': self.cleaned_data[key]
                }
                payload['datum_set'].append(datum)
            payload['state'] = models.DataSet.DataSetState.INGESTING
            return payload
        else:
            raise RuntimeError("Trying to serialize contents of invalid form")

class IngestCommitForm(IngestForm):
    commit = forms.ChoiceField(label='Commit to datastore', choices=[(True, 'Commit'), (False, 'Discard')])

    def clean_commit(self):
        # guard against using this form to discard already-committed data
        try:
            models.DataSet.objects.get(
                identifier=payload['identifier'],
                owner=self.user,
                state=models.DataSet.DataSetState.AWAITING_COMMIT
            )
        except models.DataSet.DoesNotExist:
            raise ValidationError(f"No matching dataset awaiting commit")

    def to_serializer_payload(self):
        payload = super().to_serializer_payload()
        payload['state'] = models.DataSet.DataSetState.COMMITTED
        return payload
