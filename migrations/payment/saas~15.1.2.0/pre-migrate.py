from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "payment.link.wizard", "acquirer_id")
