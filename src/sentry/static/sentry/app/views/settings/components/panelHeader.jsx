import {Flex} from 'grid-emotion';
import PropTypes from 'prop-types';
import React from 'react';
import styled from 'react-emotion';
import styles from '../../../styles/index';

const StyledPanelHeader = styled(({disablePadding, hasButtons, ...props}) => (
  <Flex align="center" justify="space-between" {...props} />
))`
  color: ${p => (p.lightText ? p.theme.gray2 : p.theme.gray3)};
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  border-bottom: 1px solid ${p => p.theme.borderDark};
  border-radius: ${p => p.theme.borderRadius} ${p => p.theme.borderRadius} 0 0;
  background: ${p => p.theme.offWhite};
  line-height: 1;

  ${p => (p.hasButtons ? styles.paddingVertical(2) : styles.paddingVertical(4))};
  ${p => !p.disablePadding && styles.paddingHorizontal(4)};
  ${p => p.hasButtons && styles.paddingRight(2)};
`;

class PanelHeader extends React.Component {
  static propTypes = {
    disablePadding: PropTypes.bool,
    hasButtons: PropTypes.bool,
    lightText: PropTypes.bool,
    ...Flex.propTypes,
  };

  render() {
    return <StyledPanelHeader {...this.props} />;
  }
}

export default PanelHeader;
