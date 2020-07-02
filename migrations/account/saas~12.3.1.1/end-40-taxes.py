# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "tax_accounts_v12_bckp"):
        cr.execute("DROP TABLE financial_report_lines_v12_bckp")
        cr.execute("DROP TABLE account_tax_account_tag_v12_bckp")
        cr.execute("DROP TABLE tax_accounts_v12_bckp")
        cr.execute("DROP TABLE financial_tags_conversion_map")
        cr.execute("DROP TABLE v12_financial_tags_registry")
        cr.execute("DROP TABLE taxes_not_to_merge")
        cr.execute("DROP TABLE caba_aml_invoice_info")
        cr.execute("DROP TABLE tags_to_replace")
