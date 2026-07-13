import pytest

from open_webui.routers.auths import _normalize_ldap_server_config


class TestNormalizeLdapServerConfig:
    def test_normalizes_full_config(self):
        server = {
            'label': 'Primary',
            'host': 'ldap1.example.com',
            'port': 389,
            'attribute_for_mail': 'mail',
            'attribute_for_username': 'uid',
            'app_dn': 'cn=app,dc=example,dc=com',
            'app_dn_password': 'secret',
            'search_base': 'ou=users,dc=example,dc=com',
            'search_filters': '(objectClass=person)',
            'use_tls': True,
            'certificate_path': '/tmp/ca.pem',
            'validate_cert': False,
            'ciphers': 'ALL',
        }
        result = _normalize_ldap_server_config(server)

        assert result['host'] == 'ldap1.example.com'
        assert result['label'] == 'Primary'
        assert result['app_dn'] == 'cn=app,dc=example,dc=com'
        assert result['app_dn_password'] == 'secret'
        assert result['use_tls'] is True
        assert result['validate_cert'] is False

    def test_handles_missing_fields_with_defaults(self):
        server = {
            'label': 'Minimal',
            'host': 'ldap2.example.com',
        }
        result = _normalize_ldap_server_config(server)

        assert result['host'] == 'ldap2.example.com'
        assert result['label'] == 'Minimal'
        assert result['attribute_for_mail'] == 'mail'
        assert result['attribute_for_username'] == 'uid'
        assert result['use_tls'] is True
        assert result['validate_cert'] is True
        assert result['ciphers'] == 'ALL'

    def test_handles_none_input(self):
        result = _normalize_ldap_server_config(None)
        assert result == {}

    def test_handles_non_dict_input(self):
        result = _normalize_ldap_server_config('not a dict')
        assert result == {}

    def test_handles_app_password_alias(self):
        server = {
            'label': 'Alias',
            'host': 'ldap.example.com',
            'app_password': 'fallback_secret',
        }
        result = _normalize_ldap_server_config(server)

        assert result['app_dn_password'] == 'fallback_secret'

    def test_handles_empty_values(self):
        server = {
            'label': '',
            'host': '',
            'port': None,
        }
        result = _normalize_ldap_server_config(server)

        assert result['label'] == ''
        assert result['host'] == ''
        assert result['port'] is None
