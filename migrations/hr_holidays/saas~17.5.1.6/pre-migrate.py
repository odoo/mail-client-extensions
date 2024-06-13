from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(cr, "hr.leave", "state", {"draft": "cancel"})
