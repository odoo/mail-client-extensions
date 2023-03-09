# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "account_invoice_extract.account_invoice_extract_endpoint")

    iap_extract = util.import_script("iap_extract/saas~16.2.1.0/end-migrate.py")
    iap_extract.migrate_status_code(cr, "account.move")
    iap_extract.migrate_document_uuid(cr, "account.move")
