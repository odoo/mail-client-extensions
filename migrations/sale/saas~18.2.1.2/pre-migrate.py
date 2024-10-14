from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "sale.order.cancel")
    util.remove_record(cr, "sale.mail_template_sale_cancellation")
