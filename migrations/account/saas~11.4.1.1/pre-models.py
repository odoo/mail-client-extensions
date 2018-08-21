# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_invoice", "vendor_bill_id", "int4")
    util.create_column(cr, "account_invoice", "vendor_display_name", "varchar")

    util.create_column(cr, "account_chart_template", "transfert_account_code_prefix", "varchar")
    cr.execute(
        """
        UPDATE account_chart_template c
           SET transfert_account_code_prefix = a.code
          FROM account_account_template a
         WHERE a.id = c.transfer_account_id
        """
    )

    cr.execute("DELETE FROM wizard_multi_charts_accounts")

    util.remove_field(cr, "account.move.line", "is_unaffected_earning_line")
    util.remove_field(cr, "account.chart.template", "company_id")
    util.remove_field(cr, "account.chart.template", "transfert_account_id")
    util.remove_field(cr, "wizard.multi.charts.accounts", "transfer_account_id")
    util.remove_field(cr, "account.tax.template", "company_id")

    util.remove_model(cr, "account.opening")
