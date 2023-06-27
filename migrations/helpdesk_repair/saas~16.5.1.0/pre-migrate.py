# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_repair.helpdesk_team_view_form_inherit_helpdesk_repair")
    util.remove_view(cr, "helpdesk_repair.view_repair_order_form_inherit_helpdesk_repair")
