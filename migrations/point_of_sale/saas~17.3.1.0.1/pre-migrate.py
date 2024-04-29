from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "pos.category", "child_id", "child_ids")
    util.remove_field(cr, "pos.session", "cash_register_total_entry_encoding")
