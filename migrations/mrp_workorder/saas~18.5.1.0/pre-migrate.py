from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.workorder", "lot_id")
    util.rename_field(cr, "quality.check", "finished_lot_id", "finished_lot_ids")
