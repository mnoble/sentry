from __future__ import absolute_import

from sentry.api.bases.organization import (
    OrganizationEndpoint, OrganizationIntegrationsPermission
)
from sentry.api.paginator import OffsetPaginator
from sentry.api.serializers import serialize
from sentry.models import OrganizationIntegration


class OrganizationIntegrationsEndpoint(OrganizationEndpoint):
    permission_classes = (OrganizationIntegrationsPermission, )

    def get(self, request, organization):
        integrations = OrganizationIntegration.objects.filter(
            organization=organization
        )

        if 'provider_key' in request.GET:
            provider_key = request.GET['provider_key']

            if provider_key == 'vsts':
                integrations = integrations.filter(
                    integration__provider__in=('vsts', 'vsts-extension'),
                )
            else:
                integrations = integrations.filter(
                    integration__provider=provider_key,
                )

        return self.paginate(
            queryset=integrations,
            request=request,
            order_by='integration__name',
            on_results=lambda x: serialize(x, request.user),
            paginator_cls=OffsetPaginator,
        )
