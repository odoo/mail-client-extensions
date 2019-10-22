# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.column_exists(cr, "account_invoice", "l10n_in_export_type"):
        # new columns added in saas-12.1
        util.create_column(cr, "account_move", "l10n_in_export_type", "varchar")
        util.create_column(cr, "account_move", "l10n_in_shipping_bill_number", "varchar")
        util.create_column(cr, "account_move", "l10n_in_shipping_bill_date", "date")
        util.create_column(cr, "account_move", "l10n_in_shipping_port_code_id", "int4")
        util.create_column(cr, "account_move", "l10n_in_reseller_partner_id", "int4")

        cr.execute(
            """
            UPDATE account_move am
               SET l10n_in_export_type = inv.l10n_in_export_type,
                   l10n_in_shipping_bill_number = inv.l10n_in_shipping_bill_number,
                   l10n_in_shipping_bill_date = inv.l10n_in_shipping_bill_date,
                   l10n_in_shipping_port_code_id = inv.l10n_in_shipping_port_code_id,
                   l10n_in_reseller_partner_id = inv.l10n_in_reseller_partner_id
              FROM account_invoice inv
             WHERE am.id = inv.move_id
        """
        )
