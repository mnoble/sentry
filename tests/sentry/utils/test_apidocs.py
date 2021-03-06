from __future__ import absolute_import
from sentry.utils import apidocs


def test_simplify_regex():
    out = apidocs.simplify_regex(r'^/organizations/(?P<org_id>\w+)/$')
    assert out == '/organizations/{org_id}/'

    out = apidocs.simplify_regex(r'^/orgs/(?P<org_id>[\w]+)/project/(?P<id>[\d]+)/$')
    assert out == '/orgs/{org_id}/project/{id}/'


def test_parse_doc_string():
    text = """
Glory!
~~~~~~

This is a glorious function

:param int id: An id.
:qparam bool louder: Make it louder?
:pparam string orgid: The orgid
:auth: required
"""
    result = apidocs.parse_doc_string(text)
    assert result[0] == 'Glory!'
    assert result[1] == ['This is a glorious function']
    params = result[2]
    assert 'path' in params, 'Should have path params'
    assert params['path'][0] == dict(name='orgid', type="string",
                                     description='The orgid')
    assert 'query' in params, 'Should have query params'
    assert params['query'][0] == dict(name='louder', type="bool",
                                     description='Make it louder?')
    assert 'auth' in params, 'Should have auth'
    assert params['auth'][0] == dict(name='', type="", description='required')

    assert 'param' in params, 'Should have regular param'
    assert params['param'][0] == dict(name='id', type="int",
                                     description='An id.')


def test_camelcase_to_dashes():
    result = apidocs.camelcase_to_dashes('CamelCase')
    assert result == 'camel-case'

    result = apidocs.camelcase_to_dashes('CaCa')
    assert result == 'ca-ca'

    result = apidocs.camelcase_to_dashes('CCM')
    assert result == 'CCM'
