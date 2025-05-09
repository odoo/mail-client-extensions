from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "bank.rec.widget")
    util.remove_model(cr, "bank.rec.widget.line")
