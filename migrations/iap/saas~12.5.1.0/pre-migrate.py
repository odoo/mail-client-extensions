# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_m2m(cr, "iap_account_res_company_rel", "iap_account", "res_company")
    cr.execute(
        """
        INSERT INTO iap_account_res_company_rel(iap_account_id, res_company_id)
             SELECT iap.id, COALESCE(iap.company_id, p.company_id)
               FROM iap_account iap
            JOIN res_users u ON u.id = iap.create_uid
            JOIN res_partner p ON p.id = u.partner_id
    """
    )
    util.remove_column(cr, "iap_account", "company_id")
    util.rename_field(cr, "iap.account", "company_id", "company_ids")
