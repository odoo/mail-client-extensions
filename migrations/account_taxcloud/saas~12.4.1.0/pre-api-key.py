# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "taxcloud_api_id", "varchar")
    util.create_column(cr, "res_company", "taxcloud_api_key", "varchar")
    util.remove_column(cr, "res_config_settings", "taxcloud_api_id")  # field now a related
    util.remove_column(cr, "res_config_settings", "taxcloud_api_key")

    cr.execute(
        """
        DELETE FROM ir_config_parameter
              WHERE "key" IN ('account_taxcloud.taxcloud_api_id', 'account_taxcloud.taxcloud_api_key')
          RETURNING substr("key", 31), value
    """
    )

    params = dict(cr.fetchall())
    if params:
        cr.execute(
            "UPDATE res_company SET taxcloud_api_id = %s, taxcloud_api_key = %s", [params.get("id"), params.get("key")]
        )

    util.remove_record(cr, "account_taxcloud.action_account_invoice_update_taxes")
