# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "payment_sepa_direct_debit.mail_template_sepa_notify_debit", util.update_record_from_xml)
    util.if_unchanged(cr, "payment_sepa_direct_debit.mail_template_sepa_notify_validation", util.update_record_from_xml)
