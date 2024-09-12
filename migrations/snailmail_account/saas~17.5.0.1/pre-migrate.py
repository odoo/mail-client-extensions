from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "invoice_is_snailmail")
    util.remove_field(cr, "res.config.settings", "invoice_is_snailmail")
