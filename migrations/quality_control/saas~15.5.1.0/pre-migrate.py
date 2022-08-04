from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr, "quality.point", "measure_on", {"operation": "product", "product": "move_line"}
    )
    util.change_field_selection_values(
        cr, "quality.check", "measure_on", {"operation": "product", "product": "move_line"}
    )
