from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "auth_passkey.rule_auth_passkey_key_user", fields=["groups"])
    util.force_noupdate(cr, "auth_passkey.rule_auth_passkey_key_user", noupdate=True)
    util.force_noupdate(cr, "auth_passkey.rule_auth_passkey_key_admin", noupdate=True)
