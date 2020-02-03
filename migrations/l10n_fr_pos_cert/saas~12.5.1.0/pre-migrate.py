# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_fr_pos_cert.action_check_hash_integity_pos_orders")
    util.remove_record(cr, "l10n_fr_pos_cert.menu_check_pos_order_integrity")
    util.remove_record(cr, "l10n_fr_pos_cert.access_l10n_fr_sale_closing_account_sale_closing_user")

    util.rename_field(cr, "account.sale.closing", "last_move_hash", "last_order_hash")
    util.create_column(cr, "account_sale_closing", "last_order_id", "int4")
    cr.execute(
        """
        UPDATE account_sale_closing g
           SET last_order_id = o.id
          FROM pos_order o
         WHERE g.last_move_id = o.account_move
    """
    )
    util.remove_field(cr, "account.sale.closing", "last_move_id")
