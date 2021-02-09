# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "utm.campaign", "is_website", "is_auto_campaign")
