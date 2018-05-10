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
import sentryApp from 'app/data/forms/sentryApp';
import {t} from 'app/locale';

class SentryAppDetails extends AsyncView {
  static contextTypes = {
    router: PropTypes.object.isRequired,
  };

  getTitle() {
    return 'Sentry App Details';
  }

  get title() {
    return this.state.app.name;
  }

  getDefaultState() {
    return {
      loading: true,
      error: false,
      app: null,
      errors: {},
    };
  }

  getEndpoints() {
    return [['app', `/sentry-apps/${this.props.params.slug}/`]];
  }

  updateSentryApp(data) {
    this.api.request(`/sentry-apps/${this.props.params.slug}/`, {
      method: 'PUT',
      data: {
        name: data.name,
        scopes: data.scopes,
        webhook_url: data.webhook_url,
      },
      success: app => {
        addSuccessMessage('Sentry App updated.');
      },
      error: error => {
        addErrorMessage(t(error.responseJSON.error));
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
          method="PUT"
          className="form-stacked"
          onSubmit={this.updateSentryApp.bind(this)}
          onCancel={this.cancel.bind(this)}
          initialData={this.state.app}
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

export default SentryAppDetails;
