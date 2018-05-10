import {Box} from 'grid-emotion';
import PropTypes from 'prop-types';
import React from 'react';

import {addErrorMessage, addSuccessMessage} from 'app/actionCreators/indicator';
import ApiScopesField from 'app/views/settings/components/forms/apiScopesField';
import AsyncView from 'app/views/asyncView';
import Form from 'app/views/settings/components/forms/form';
import JsonForm from 'app/views/settings/components/forms/jsonForm';
import {Panel, PanelBody, PanelHeader} from 'app/components/panels';
import SettingsPageHeader from 'app/views/settings/components/settingsPageHeader';
import {t} from 'app/locale';
import sentryApp from 'app/data/forms/sentryApp';

class NewSentryApp extends AsyncView {
  static contextTypes = {
    router: PropTypes.object.isRequired,
  };

  get title() {
    return 'New Sentry App';
  }

  get endpoint() {
    return '/sentry-apps';
  }

  get blankSentryApp() {
    return {
      scopes: [],
      name: '',
      homepage_url: '',
      privacy_url: '',
      terms_url: '',
    };
  }

  createSentryApp(data) {
    this.api.request('/sentry-apps/', {
      method: 'POST',
      data: {
        name: data.name,
        scopes: data.scopes,
        webhook_url: data.webhook_url,
      },
      success: app => {
        addSuccessMessage('Sentry App created.');
        this.context.router.push(`/settings/account/api/sentry-apps/${app.slug}`);
      },
      error: error => {
        addErrorMessage(t('Unable to create Sentry App.'));
      },
    });
  }

  cancel() {
    this.context.router.push('/settings/account/api/sentry-apps/');
  }

  renderBody() {
    return (
      <div>
        <SettingsPageHeader title={this.title} />

        <Form
          method="POST"
          className="form-stacked"
          onSubmit={this.createSentryApp.bind(this)}
          onCancel={this.cancel.bind(this)}
          initialData={this.blankSentryApp}
        >
          <Box>
            <JsonForm location={this.props.location} forms={sentryApp} />

            <Panel>
              <PanelHeader>{t('Permissions')}</PanelHeader>
              <PanelBody>
                <ApiScopesField name="scopes" />
              </PanelBody>
            </Panel>
          </Box>
        </Form>
      </div>
    );
  }
}

export default NewSentryApp;
