from __future__ import absolute_import

from django import forms
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from sentry.integrations.pipeline import IntegrationPipeline
from sentry.models import Organization
from sentry.web.frontend.base import BaseView


class VstsExtensionConfigurationForm(forms.Form):
    organization = forms.ChoiceField(
        label=_('Organization'),
        choices=(),
        required=True,
        widget=forms.Select(),
    )

    vsts_id = forms.CharField(
        widget=forms.HiddenInput(),
    )

    vsts_name = forms.CharField(
        widget=forms.HiddenInput(),
    )

    def __init__(self, request=None, organizations=None, *args, **kwargs):
        super(VstsExtensionConfigurationForm, self).__init__(*args, **kwargs)

        self.fields['vsts_id'].initial = request.GET['targetId']
        self.fields['vsts_name'].initial = request.GET['targetName']
        self.fields['organization'].initial = request.session.get('activeorg')
        self.fields['organization'].choices = [
            (o.slug, o.name) for o in request.user.get_orgs()
        ]


class VstsExtensionConfigurationView(BaseView):
    auth_required = False

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            configure_uri = '{}?{}'.format(
                reverse('vsts-extension-configuration'),
                urlencode({
                    'targetId': request.GET['targetId'],
                    'targetName': request.GET['targetName'],
                }),
            )

            redirect_uri = '{}?{}'.format(
                reverse('sentry-login'),
                urlencode({'next': configure_uri}),
            )

            return self.redirect(redirect_uri)

        if request.user.get_orgs().count() == 1:
            org = request.user.get_orgs()[0]

            pipeline = self.init_pipeline(
                request,
                org,
                request.GET['targetId'],
                request.GET['targetName'],
            )

            return pipeline.current_step()
        else:
            return self.respond('sentry/vsts-organization-link.html', {
                'vsts_form': VstsExtensionConfigurationForm(request),
            })

    def post(self, request, *args, **kwargs):
        # Update Integration with Organization chosen
        org = Organization.objects.get(
            slug=request.POST['organization'],
        )

        pipeline = self.init_pipeline(
            request,
            org,
            request.POST['vsts_id'],
            request.POST['vsts_name'],
        )

        return pipeline.current_step()

    def init_pipeline(self, request, organization, id, name):
        pipeline = IntegrationPipeline(
            request=request,
            organization=organization,
            provider_key='vsts-extension',
        )

        pipeline.initialize()
        pipeline.bind_state('vsts', {
            'AccountId': id,
            'AccountName': name,
        })

        return pipeline
