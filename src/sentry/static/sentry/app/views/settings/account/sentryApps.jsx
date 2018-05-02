import {Box, Flex} from 'grid-emotion';
import PropTypes from 'prop-types';
import React from 'react';
import {Link} from 'react-router';

import AsyncView from 'app/views/asyncView';
import Button from 'app/components/buttons/button';
import EmptyMessage from 'app/views/settings/components/emptyMessage';
import {Panel, PanelBody, PanelHeader, PanelItem} from 'app/components/panels';
import SettingsPageHeader from 'app/views/settings/components/settingsPageHeader';
import Avatar from 'app/components/avatar';
import {t} from 'app/locale';

const ROUTE_PREFIX = '/settings/account/api/sentry-apps/';

class SentryAppRow extends AsyncView {
  static contextTypes = {
    router: PropTypes.object.isRequired,
  };

  static propTypes = {
    app: PropTypes.object.isRequired,
  };

  onRemove() {
    // TODO
  }

  renderBody() {
    let app = this.props.app;

    return (
      <PanelItem justify="space-between" px={2} py={2}>
        <Flex align="center">
          <Box pr={10}>
            <Avatar model={app} />
          </Box>
        </Flex>

        <Box flex="1">
          <h4>
            <Link to={`${ROUTE_PREFIX}${app.slug}/`}>{app.name}</Link>
          </h4>
        </Box>
      </PanelItem>
    );
  }
}

class SentryAppRowCollection extends AsyncView {
  static contextTypes = {
    router: PropTypes.object.isRequired,
  };

  static propTypes = {
    apps: PropTypes.arrayOf(PropTypes.object),
  };

  renderBody() {
    if (this.props.apps.length === 0) {
      return <EmptyMessage>{t("You haven't created any Sentry Apps yet.")}</EmptyMessage>;
    } else {
      return (
        <div>{this.props.apps.map(app => <SentryAppRow key={app.uuid} app={app} />)}</div>
      );
    }
  }
}

class SentryApps extends AsyncView {
  static contextTypes = {
    router: PropTypes.object.isRequired,
  };

  getEndpoints() {
    return [['appList', '/sentry-apps/']];
  }

  newSentryApp() {
    this.context.router.push('/settings/account/api/sentry-apps/new/');
  }

  removeSentryApp(app) {
    this.setState({
      appList: this.state.appList.filter(a => a.id !== app.id),
    });
  }

  get title() {
    return 'Sentry Apps';
  }

  get newSentryAppButton() {
    return (
      <Button
        priority="primary"
        size="small"
        className="ref-new-sentry-app"
        onClick={this.newSentryApp.bind(this)}
      >
        {t('Create Sentry App')}
      </Button>
    );
  }

  renderBody() {
    return (
      <div>
        <SettingsPageHeader title={this.title} action={this.newSentryAppButton} />

        <Panel>
          <PanelHeader disablePadding>
            <Flex align="center">
              <Box px={2} flex="1">
                {t('Name')}
              </Box>
            </Flex>
          </PanelHeader>

          <PanelBody>
            <SentryAppRowCollection apps={this.state.appList} />
          </PanelBody>
        </Panel>
      </div>
    );
  }
}

export default SentryApps;
