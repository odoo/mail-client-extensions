# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record_if_unchanged(cr, "purchase.email_template_edi_purchase")
    util.remove_record_if_unchanged(cr, "purchase.email_template_edi_purchase_done")
