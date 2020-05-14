# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    imp = util.import_script("base/saas~12.5.1.3/pre-41-read_group.py")
    imp.refactor_read_group(cr, "account_tax", "python_compute")
    imp.refactor_read_group(cr, "account_tax", "python_applicable")
    imp.refactor_read_group(cr, "account_tax_template", "python_compute")
    imp.refactor_read_group(cr, "account_tax_template", "python_applicable")
