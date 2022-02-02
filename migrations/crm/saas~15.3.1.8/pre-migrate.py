# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.lead", "user_email")
    util.remove_field(cr, "crm.lead", "user_login")
