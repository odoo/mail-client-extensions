# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # This view has been replaced by an inclusion
    # in web.qunit.suite_tests, in the manifest
    util.remove_view(cr, 'documents_spreadsheet.qunit_suite')
