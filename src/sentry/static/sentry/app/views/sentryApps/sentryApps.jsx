import React from 'react';
import {Box, Flex} from 'grid-emotion';
import PropTypes from 'prop-types';

import {addErrorMessage, addSuccessMessage} from 'app/actionCreators/indicator';
import {t} from 'app/locale';
import AsyncComponent from 'app/components/asyncComponent';
import Avatar from 'app/components/avatar';
import {Panel, PanelItem, PanelHeader, PanelBody} from 'app/components/panels';
import Switch from 'app/components/switch';
import SentryTypes from 'app/proptypes';

class SentryAppRow extends AsyncComponent {
  static propTypes = {
    ...SentryTypes.SentryApp,
    organization: PropTypes.object.isRequired,
  };

  installToggle() {
    if (this.props.installed) {
      this.wasUninstalled();
    } else {
      this.api.request(
        `/organizations/${this.props.organization.slug}/sentry-app-installations/`,
        {
          method: 'POST',
          data: {slug: this.props.slug},
          success: app => this.wasInstalled(),
          error: error => this.failedToInstall(),
        }
      );
    }
  }

  wasUninstalled() {
    this.props.installed = false;
  }

  wasInstalled() {
    addSuccessMessage(`${this.props.slug} installed.`);
  }

  failedToInstall() {
    addErrorMessage(`${this.props.slug} failed to install.`);
  }

  failedToUninstall() {
    addErrorMessage(`${this.props.slug} failed to uninstall.`);
  }

  renderBody() {
    let {uuid, name, installed} = this.props;

    return (
      <PanelItem key={uuid}>
        <Flex align="center">
          <Box pr={10} flex="1" align="center">
            <Avatar model={this.props} />
          </Box>
        </Flex>

        <Box flex="1">{name}</Box>

        <Box>
          <Switch isActive={installed} size="lg" toggle={this.installToggle.bind(this)} />
        </Box>
      </PanelItem>
    );
  }
}

export default class SentryApps extends AsyncComponent {
  static propTypes = {
    orgId: PropTypes.string.isRequired,
  };

  getEndpoints() {
    let {orgId} = this.props;

    return [
      ['sentryApps', '/sentry-apps/'],
      ['installs', `/organizations/${orgId}/sentry-app-installations/`],
      ['organization', `/organizations/${orgId}/`],
    ];
  }

  isInstalled(sentryApp) {
    return this.state.installs.some(i => i.sentry_app.slug == sentryApp.slug);
  }

  get features() {
    return new Set(this.state.organization.features);
  }

  renderBody() {
    if (!this.features.has('sentry-apps')) {
      return '';
    }

    const sentryApps = this.state.sentryApps.map(app => (
      <SentryAppRow
        {...app}
        installed={this.isInstalled(app)}
        organization={this.state.organization}
        key={app.uuid}
      />
    ));

    return (
      <Panel>
        <PanelHeader disablePadding={true}>
          <Box px={2} flex="1">
            {t('Sentry Apps')}
          </Box>
          <Box flex="1" />
          <Box mr={15}>{t('Installed')}</Box>
        </PanelHeader>
        <PanelBody>{sentryApps}</PanelBody>
      </Panel>
    );
  }
}
