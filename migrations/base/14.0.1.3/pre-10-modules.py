# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.new_module(cr, "adyen_platforms", deps={"mail", "web"})
    util.new_module(cr, "payment_odoo_by_adyen", deps={"payment", "adyen_platforms"})
    util.module_deps_diff(cr, "pos_adyen", plus={"adyen_platforms"})
    util.new_module(cr, "payment_fix_register_token", deps={"payment"}, auto_install=True)

    # deps chamged by odoo/odoo@59d16513a019d52dd090e09c09be4675aa868baf (odoo/odoo#62730)
    util.module_deps_diff(cr, "l10n_be_edi", plus={"account_edi_ubl"}, minus={"account_edi"})

    if util.has_enterprise():
        util.new_module(cr, "account_reports_tax", deps={"account_reports"}, auto_install=True)

    util.remove_module(cr, "website_gengo")
    util.remove_module(cr, "base_gengo")
