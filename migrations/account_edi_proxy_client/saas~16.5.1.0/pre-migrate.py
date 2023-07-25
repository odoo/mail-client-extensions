# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(
        cr, "account_edi_proxy_client_user", "account_edi_proxy_client_user_unique_edi_identification"
    )
    util.remove_constraint(cr, "account_edi_proxy_client_user", "account_edi_proxy_client_user_unique_company_proxy")
