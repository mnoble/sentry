from __future__ import absolute_import

from time import sleep

from sentry.mediators.sentry_apps import Creator
from sentry.models import SentryApp
from sentry.testutils import AcceptanceTestCase


class SentryAppsTest(AcceptanceTestCase):
    def setUp(self):
        super(SentryAppsTest, self).setUp()

        self.user = self.create_user()
        self.org = self.create_organization()
        self.create_member(user=self.user, organization=self.org, role='owner')
        self.sentry_app = Creator.run(
            name='SlowDB',
            user=self.user,
            scopes=('project:write', ),
            webhook_url='http://example.com',
        )

        self.login_as(self.user)

        self.sentry_apps_path = '/settings/account/api/sentry-apps/'
        self.new_sentry_app_path = '/settings/account/api/sentry-apps/new/'

    def test_create_sentry_app(self):
        self.browser.get(self.sentry_apps_path)
        self.browser.wait_until_not('.loading-indicator')
        self.browser.snapshot('account settings - sentry apps - empty list')

        self.browser.click('.ref-new-sentry-app')
        self.browser.wait_until_not('.loading-indicator')

        assert self.browser.current_url.endswith(self.new_sentry_app_path)

        self.browser.snapshot('account settings - sentry apps - create')
        self.browser.element('input[name="name"]').send_keys('NullDB')
        self.browser.element('input[name="webhook_url"]') \
            .send_keys('http://example.com')
        self.browser.element('input[value="project:read"]').click()
        self.browser.click('[data-test-id="form-submit"]')
        sleep(1)

        sentry_app = SentryApp.objects.get(slug='null-db')
        assert sentry_app.name == 'NullDB'
        assert sentry_app.webhook_url == 'http://example.com'
        assert sentry_app.get_scopes() == ['project:read']

    def test_update_sentry_app(self):
        self.browser.get(self.sentry_apps_path)
        self.browser.snapshot('ASDASDASD')
        self.browser.driver.find_element_by_link_text('SlowDB').click()

        self.browser.wait_until('input[name="webhook_url"]')
        self.browser.snapshot('account settings - sentry apps - details')

        self.browser.element('input[name="webhook_url"]').clear()
        self.browser.element('input[name="webhook_url"]').send_keys(
            'http://example.com/webhook'
        )

        self.browser.click('[data-test-id="form-submit"]')
        sleep(1)

        sentry_app = SentryApp.objects.get(slug='slow-db')
        assert sentry_app.webhook_url == 'http://example.com/webhook'
