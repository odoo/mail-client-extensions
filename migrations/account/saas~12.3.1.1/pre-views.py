# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    The view `account.view_account_bank_journal_form` exists in Odoo from 9.0
    to 13.0 but temporary disappears in saas-12.3. After discussion with the accounting team,
    it appears that this view came back in 13.0 but as dead code (this view is not used).
    So, this view will probably disappear again in 14.0.
    By consequence, it's useless to keep any view customisation and the best solution is to
    drop this view.
    """
    util.remove_record(cr, "account.view_account_bank_journal_form")
