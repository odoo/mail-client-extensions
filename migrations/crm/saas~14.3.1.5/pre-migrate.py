# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.lead", "ribbon_message")
    util.create_column(cr, "crm_team_member", "assignment_optout", "boolean")
