import os.path
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.urls import reverse
import fsspec
import irods_fsspec
from .forms import IngestPathVerifyForm, IngestForm
from .. import cyverse

@login_required
def overview(request):
    return render(request, 'registrar/overview.html')

@login_required
def ingest(request):
    if request.method == 'GET':
        if 'path' in request.GET:
            verify_form = IngestPathVerifyForm(request.GET)
            if not verify_form.is_valid():
                ingest_form = None
                path = request.GET['path']
            else:
                # path validated, on to step 2
                path = verify_form.cleaned_data['path']
                ingest_form = IngestForm(cleaned_irods_path=path)
                verify_form = None
        else:
            # Use unbound form when there is no param to validate
            verify_form = IngestPathVerifyForm()
            ingest_form = None
            path = None
    elif request.method == 'POST':
        verify_form = None
        ingest_form = IngestForm(request.POST)
        if ingest_form.is_valid():
            # launch ingest
            return HttpResponseRedirect(reverse('registrar_overview'))
    else:
        raise HttpResponseNotAllowed(['GET', 'POST'])

    return render(request, 'registrar/ingest.html', {
        'verify_form': verify_form,
        'ingest_form': ingest_form,
        'path': path
    })
