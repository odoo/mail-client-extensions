# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "calendar_contacts", "partner_checked", "bool", default=True)
