from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "planning.slot", "template_duration_days")
