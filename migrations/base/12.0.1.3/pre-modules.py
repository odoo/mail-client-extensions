# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "l10n_it_edi", deps={"l10n_it"})  # see odoo/odoo#30845
