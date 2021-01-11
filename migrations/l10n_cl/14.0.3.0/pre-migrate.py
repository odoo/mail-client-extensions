# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_cl.view_account_journal_form_inherit_l10n_cl")
