from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move", "extracted_word_ids")
