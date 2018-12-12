# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, "account._assets_backend_helpers", "account._assets_primary_variables")
    util.remove_view(cr, "account.res_company_form_view_inherit_account_intrastat")
