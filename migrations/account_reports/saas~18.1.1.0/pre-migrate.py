from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "totals_below_sections")
    util.remove_field(cr, "res.config.settings", "totals_below_sections")
