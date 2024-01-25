from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "planning.slot", "working_days_count")
    util.remove_field(cr, "planning.analysis.report", "working_days_count")
