# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "industry_fsm.portal_my_worksheet")
    util.remove_field(cr, "project.task", "has_complete_partner_address")
