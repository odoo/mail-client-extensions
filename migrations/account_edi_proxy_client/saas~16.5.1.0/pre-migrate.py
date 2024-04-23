from odoo.upgrade import util


def migrate(cr, version):
    if util.parse_version(version) >= util.parse_version("saas~16.3"):
        util.remove_constraint(
            cr, "account_edi_proxy_client_user", "account_edi_proxy_client_user_unique_edi_identification"
        )
        util.remove_constraint(
            cr, "account_edi_proxy_client_user", "account_edi_proxy_client_user_unique_company_proxy"
        )
