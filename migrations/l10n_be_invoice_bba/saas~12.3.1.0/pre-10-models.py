# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", 'l10n_be_structured_comm')
    util.remove_field(cr, "res.config.settings", 'l10n_be_structured_comm')
    util.remove_view(cr, 'l10n_be_invoice_bba.res_config_settings_view_form')
