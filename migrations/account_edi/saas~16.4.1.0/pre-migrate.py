from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "account_edi.action_open_payment_edi_documents")
    util.remove_view(cr, "account_edi.view_payment_form_inherit")
