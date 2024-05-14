from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "mrp_workorder.action_work_order_mark_as_done")
