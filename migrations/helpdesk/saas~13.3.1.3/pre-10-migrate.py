# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "helpdesk_visibility_team", "helpdesk_team", "res_users")
