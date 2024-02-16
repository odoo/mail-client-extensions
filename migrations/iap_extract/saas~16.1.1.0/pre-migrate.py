# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "account_invoice_extract.account_invoice_extract_no_credit",
        "iap_extract.iap_extract_no_credit",
        noupdate=False,
    )
