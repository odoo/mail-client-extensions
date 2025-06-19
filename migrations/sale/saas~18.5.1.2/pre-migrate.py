from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "sale.payment.provider.onboarding.wizard")
    util.delete_unused(cr, "sale.mt_salesteam_invoice_created")
    util.rename_xmlid(cr, "sale.mt_salesteam_invoice_confirmed", "sale.mt_salesteam_invoice_posted")
    util.if_unchanged(cr, "sale.mt_salesteam_invoice_posted", util.update_record_from_xml)
