# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "documents.documents_invoice_png", "documents.documents_mail_png")

    util.force_noupdate(cr, "documents.mail_template_document_request", noupdate=True)
