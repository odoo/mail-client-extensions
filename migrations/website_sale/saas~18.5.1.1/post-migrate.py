from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_sale.checkout_step_payment", util.update_record_from_xml)
