from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(
        cr, "account_edi_proxy_client_user", "account_edi_proxy_client_user_unique_active_edi_identification"
    )
