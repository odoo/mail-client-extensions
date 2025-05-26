from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "planning.slot", "template_duration_days")
    util.remove_view(cr, "planning.resource_planning")
