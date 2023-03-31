# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_disallowed_expenses_fleet.disallowed_expenses_fleet_search_template_extra_options")
    util.remove_view(cr, "account_disallowed_expenses_fleet.disallowed_expenses_fleet_search_template")
