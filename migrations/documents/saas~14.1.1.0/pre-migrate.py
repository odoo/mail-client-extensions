# -*- coding:utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    """
    upgrade script for Master documents onboarding adjustements.
    ENT PR: 12720
    """

    # rename xml_id
    util.rename_xmlid(cr, "documents.documents_invoice_png", "documents.documents_mail_png")
