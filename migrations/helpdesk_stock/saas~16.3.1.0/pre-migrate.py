# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_stock.helpdesk_team_view_form_inherit_helpdesk_account")
