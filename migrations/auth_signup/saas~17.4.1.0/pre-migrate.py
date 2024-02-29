# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.partner", "signup_url")
    util.remove_field(cr, "res.partner", "signup_valid")
    util.remove_field(cr, "res.partner", "signup_token")
    util.remove_field(cr, "res.partner", "signup_expiration")
