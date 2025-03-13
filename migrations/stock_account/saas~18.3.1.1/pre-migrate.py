from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.valuation.layer.revaluation", "lot_id")
    util.remove_record(cr, "stock_account.action_revalue_layers")
