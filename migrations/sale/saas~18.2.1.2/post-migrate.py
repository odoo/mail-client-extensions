from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "sale.email_template_edi_sale", util.update_record_from_xml)
    util.if_unchanged(cr, "sale.email_template_proforma", util.update_record_from_xml)
    util.if_unchanged(cr, "sale.mail_template_sale_confirmation", util.update_record_from_xml)
    util.if_unchanged(cr, "sale.mail_template_sale_payment_executed", util.update_record_from_xml)
