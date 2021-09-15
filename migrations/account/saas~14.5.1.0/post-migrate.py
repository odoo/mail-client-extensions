# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "account.email_template_edi_invoice", util.update_record_from_xml)
    util.if_unchanged(cr, "account.mail_template_data_payment_receipt", util.update_record_from_xml)
    util.if_unchanged(cr, "account.email_template_edi_credit_note", util.update_record_from_xml)
