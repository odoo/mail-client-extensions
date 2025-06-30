from odoo.upgrade import util


def migrate(cr, version):
    util.make_field_non_stored(cr, "hr.employee", "additional_note", selectable=True)
