# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rt = dict(reset_translations={"subject", "body_html"})

    util.if_unchanged(cr, "l10n_cl_edi.l10n_cl_edi_email_template_invoice", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "l10n_cl_edi.email_template_receipt_ack", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "l10n_cl_edi.email_template_receipt_commercial_accept", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "l10n_cl_edi.email_template_claimed_ack", util.update_record_from_xml, **rt)
