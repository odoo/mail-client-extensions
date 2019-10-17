# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.delete_unused(cr, "account_account_type", ["l10n_ro.data_account_type_not_classified"])
