# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_account_taxcloud.res_config_settings_view_form_inherit_website_taxcloud")
