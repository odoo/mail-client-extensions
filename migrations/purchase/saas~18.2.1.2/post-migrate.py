from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "purchase.email_template_edi_purchase", util.update_record_from_xml)
    util.if_unchanged(cr, "purchase.email_template_edi_purchase_done", util.update_record_from_xml)
    util.if_unchanged(cr, "purchase.email_template_edi_purchase_reminder", util.update_record_from_xml)
