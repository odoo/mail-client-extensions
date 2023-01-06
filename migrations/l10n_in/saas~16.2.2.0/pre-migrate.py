# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, 'l10n_in.l10n_in_tcs_tds_view_partner_form')
