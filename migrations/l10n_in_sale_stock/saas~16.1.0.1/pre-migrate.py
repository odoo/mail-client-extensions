from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "stock.warehouse", "l10n_in_sale_journal_id")
    util.remove_view(cr, "l10n_in_sale_stock.view_stock_warehouse_inherit_l10n_in_stock")
