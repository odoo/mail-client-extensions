from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mail.compose.message", "record_name")
    util.make_field_non_stored(cr, "mail.message", "record_name", selectable=False)
