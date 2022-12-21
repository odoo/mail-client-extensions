# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "purchase.order", "l10n_in_journal_id")
