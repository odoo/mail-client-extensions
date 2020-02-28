# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.delete_unused(cr, "l10n_bo.account_account_type_NCLASIFICADO")
