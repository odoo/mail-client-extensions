# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "alias_id")
    util.remove_field(cr, "res.users", "alias_contact")
    util.create_column(cr, "mail_activity", "request_partner_id", "int4")
