import React from 'react';

import {API_SCOPES} from 'app/constants';
import FormField from 'app/views/settings/components/forms/formField';
import MultipleCheckbox from 'app/views/settings/components/forms/controls/multipleCheckbox';
import {t} from 'app/locale';

const API_CHOICES = API_SCOPES.map(s => [s, s]);

class ApiScopesField extends React.Component {
  static propTypes = {
    ...FormField.propTypes,
  };

  render() {
    return (
      <FormField
        name={this.props.name}
        choices={API_CHOICES}
        label={t('Scopes')}
        inline={false}
        required
      >
        {({value, onChange}) => (
          <MultipleCheckbox
            onChange={onChange}
            value={value.peek()}
            choices={API_CHOICES}
          />
        )}
      </FormField>
    );
  }
}

export default ApiScopesField;
