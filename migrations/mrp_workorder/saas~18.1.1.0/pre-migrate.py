from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "quality_check", "workcenter_id")
    util.remove_column(cr, "quality_check", "finished_lot_id")
