# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rt = dict(reset_translations={"subject", "body_html", "report_name"})

    util.if_unchanged(cr, "sale.email_template_edi_sale", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "sale.mail_template_sale_confirmation", util.update_record_from_xml, **rt)
