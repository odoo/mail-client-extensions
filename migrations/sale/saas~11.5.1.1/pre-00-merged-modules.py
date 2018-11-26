# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.parse_version(version) < util.parse_version("saas~11.4"):
        sod114 = util.import_script("sale_order_dates/saas~11.4.1.1/pre-migrate.py")
        sod114.migrate(cr, version)

        sp114 = util.import_script("sale_payment/saas~11.4.1.0/pre-migrate.py")
        sp114.migrate(cr, version, module="sale")
