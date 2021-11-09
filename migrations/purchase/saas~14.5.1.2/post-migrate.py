# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rt = dict(reset_translations={"subject", "body_html", "report_name"})

    util.if_unchanged(cr, "purchase.email_template_edi_purchase", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "purchase.email_template_edi_purchase_done", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "purchase.email_template_edi_purchase_reminder", util.update_record_from_xml, **rt)
