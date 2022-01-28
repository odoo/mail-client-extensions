# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # The `_a` action still exists in saas~12.4, but we want that the user-facing action (through the menu) keeps its ID,
    # So the users defined filters keeps working -- opw-2700213
    util.rename_xmlid(cr, *util.expand_braces("account.action_account_moves_all{_a,}"))
