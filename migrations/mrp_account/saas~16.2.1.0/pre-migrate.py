from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.workcenter.productivity", "cost_already_recorded")
