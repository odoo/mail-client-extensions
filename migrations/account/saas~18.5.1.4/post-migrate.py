from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "account.email_template_edi_invoice", util.update_record_from_xml)
