from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.bank.statement", "extracted_word_ids")
