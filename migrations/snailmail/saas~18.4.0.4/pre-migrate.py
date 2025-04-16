from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "snailmail.letter.format.error")
    util.remove_model(cr, "snailmail.letter.missing.required.fields")
