# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # odoo/enterprise#21105 (for v13 dbs created before this PR)
    util.remove_view(cr, "account_intrastat.res_config_settings_view_form")
