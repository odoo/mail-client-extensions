from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "extract.mixin.with.words", "extracted_word_ids")
    util.remove_model(cr, "iap.extracted.words")
