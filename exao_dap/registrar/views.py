import os.path
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models.fields import DateTimeField
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.urls import reverse
import fsspec
import irods_fsspec
from .forms import IngestPathVerifyForm, IngestForm
from .. import cyverse

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action, permission_classes
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import renderer_classes
from rest_framework.response import Response
from .models import Dataset, Datum
from .serializers import DatasetSerializer, DatasetInitSerializer, DatumSerializer
from .. import extensions

from rest_framework import permissions

class DatasetLimitOwnerSharedStaff(permissions.BasePermission):
    """
    Allow owner and staff/superuser to edit, additionally allow
    users with whom the dataset has been shared to read, and
    allow all to read if `public` is True
    """

    def has_object_permission(self, request, view, obj):
        can_write = request.user.is_active and (
            request.user.is_staff or
            request.user.is_superuser or
            obj.owner == request.user
        )
        can_read = (
            can_write or
            obj.public or
            (request.user.is_active and obj.shared.filter(username=request.user.username).exists())
        )
        # GET, HEAD, or OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return can_read

        # POST, etc.
        return can_write

class DatasetViewSet(extensions.BrowserFacingMixin, viewsets.ModelViewSet):
    serializer_class = DatasetSerializer
    queryset = Dataset.objects.all()
    permission_classes = [DatasetLimitOwnerSharedStaff]
    # renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    filterset_fields = {
        'identifier': ['exact', 'icontains']
    }

    def get_queryset(self):
        # unauthenticated: just public stuff
        qs = Dataset.objects.filter(public=True)
        if self.request.user.is_authenticated and self.request.user.is_active:
            # superusers: everything
            if self.request.user.is_superuser or self.request.user.is_staff:
                return self.queryset
            # normal users: things shared with them or owned by them
            return (qs |
                    Dataset.objects.filter(owner=self.request.user) |
                    Dataset.objects.filter(shared=self.request.user))
        return qs

    def retrieve(self, request, pk=None):
        if request.accepted_renderer.format == 'html':
            instance = self.get_object()
            return Response({'object': instance})
        return super().retrieve(request, pk=pk)

    def create(self, request):
        if request.accepted_renderer.format == 'html':
            verify_form = None
            ingest_form = IngestForm(request.POST, user=request.user)
            if ingest_form.is_valid():
                # rearrange data, pass into serializer to create
                # (it will) launch ingest
                ser = DatasetInitSerializer(data=ingest_form.to_serializer_payload())
                ser.is_valid(raise_exception=True)
                obj = ser.save()
                return HttpResponseRedirect(reverse('dataset-detail', args=(obj.pk,)))
            return Response(
                {'verify_form': verify_form, 'ingest_form': ingest_form, 'source_path': ingest_form.cleaned_data['source_path']},
                template_name='registrar/ingest.html'
            )
        return super().create(request)

    @action(detail=False, methods=['GET'], renderer_classes=[TemplateHTMLRenderer])
    def ingest(self, request):
        if 'source_path' in request.GET:
            verify_form = IngestPathVerifyForm(request.GET)
            print(f'{verify_form.is_valid()=}')
            if not verify_form.is_valid():
                ingest_form = None
                path = request.GET['source_path']
            else:
                # path validated, on to step 2 (
                path = verify_form.cleaned_data['source_path']
                ingest_form = IngestForm(user=request.user, cleaned_irods_path=path)
                verify_form = None
        else:
            # Use unbound form when there is no param to validate
            verify_form = IngestPathVerifyForm()
            ingest_form = None
            path = None
        return Response(
            {'verify_form': verify_form, 'ingest_form': ingest_form, 'source_path': path},
            template_name='registrar/ingest.html'
        )


class DatumViewSet(extensions.BrowserFacingMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = DatumSerializer
    queryset = Datum.objects.all()
    def get_queryset(self):
        qs = Datum.objects.filter(dataset__public=True)
        if self.request.user.is_authenticated:
            qs = (qs |
                  Datum.objects.filter(dataset__owner=self.request.user) |
                  Datum.objects.filter(dataset__shared=self.request.user))
        return qs

    @action(
        detail=False, methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def processing(self, request):
        # everywhere else, only SYNCED data are shown
        # dataset owners can see their data that's still being processed here
        # but otherwise only committed datasets are visible
        return Response(self.queryset.filter(
            dataset__owner=self.request.user,
            state__in=[Datum.DatumState.SYNCING, Datum.DatumState.NEW]
        ), template_name='datum_processing.html')

@login_required
def overview(request):
    return render(request, 'registrar/overview.html')
