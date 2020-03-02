# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_m2m(cr, "iap_account_res_company_rel", "iap_account", "res_company")
    cr.execute(
        """
        INSERT INTO iap_account_res_company_rel(iap_account_id, res_company_id)
             SELECT iap.id, iap.company_id
               FROM iap_account iap
              WHERE company_id IS NOT NULL
    """
    )
    util.remove_column(cr, "iap_account", "company_id")
    util.rename_field(cr, "iap.account", "company_id", "company_ids")
