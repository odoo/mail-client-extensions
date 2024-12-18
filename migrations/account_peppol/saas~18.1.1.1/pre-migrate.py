from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "peppol.registration", "account_peppol_migration_key")
    util.remove_field(cr, "peppol.registration", "verification_code")
    util.remove_field(cr, "account_edi_proxy_client.user", "peppol_verification_code")
    # "in_verification" is removed from account_peppol_proxy_state selection
    util.change_field_selection_values(
        cr, "res.company", "account_peppol_proxy_state", {"in_verification": "not_registered"}
    )
