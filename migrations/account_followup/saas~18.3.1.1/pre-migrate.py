from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(cr, "res.partner", "type", {"followup": "invoice"})
