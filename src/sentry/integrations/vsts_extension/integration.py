from __future__ import absolute_import

from django.contrib import messages
from django.http import HttpResponseRedirect

from sentry.integrations.vsts.integration import VstsIntegrationProvider
from sentry.pipeline import PipelineView
from sentry.utils.http import absolute_uri


class VstsExtensionIntegrationProvider(VstsIntegrationProvider):
    key = 'vsts-extension'

    def get_pipeline_views(self):
        views = super(VstsExtensionIntegrationProvider, self).get_pipeline_views()
        views[-1] = VstsExtensionFinishedView()
        return views

    def build_integration(self, state):
        # If save this data to the `identity` key in state, earlier, it gets
        # wiped out in the NestedPipeline. Instead we set it a totally
        # different key, `vsts` (see: VSTSOrganizationSelectionView) and just
        # put it where it needs to be before finishing things up.

        state['account'] = {
            'AccountId': state['vsts']['AccountId'],
            'AccountName': state['vsts']['AccountName'],
        }

        state['instance'] = '{}.visualstudio.com'.format(
            state['vsts']['AccountName']
        )

        return super(
            VstsExtensionIntegrationProvider,
            self
        ).build_integration(state)


class VstsExtensionFinishedView(PipelineView):
    def dispatch(self, request, pipeline):
        pipeline.finish_pipeline()

        messages.add_message(request, messages.SUCCESS, 'VSTS Extension installed.')

        # TODO: replace with whatever we decide the finish step is.
        return HttpResponseRedirect(
            absolute_uri('/settings/{}/integrations/vsts-extension/{}/'.format(
                pipeline.organization.slug,
                pipeline.integration.id,
            ))
        )
