# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    iap_extract = util.import_script("iap_extract/saas~16.2.1.0/end-status_code.py")
    iap_extract.migrate_status_code(cr, "account.move")
