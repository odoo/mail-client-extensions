# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for f in 'plafond_secu nombre_employes cotisation_prevoyance org_ss conv_coll'.split():
        util.remove_field(cr, 'account.config.settings', f)

    util.remove_view(cr, 'l10n_fr_hr_payroll.account_config_settings_view_form')
