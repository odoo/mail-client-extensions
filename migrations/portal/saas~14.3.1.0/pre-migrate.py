# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "portal_wizard_user", "user_id")
    util.remove_field(cr, "portal.wizard.user", "in_portal")
