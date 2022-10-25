# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.team", "amazon_team")
    util.remove_field(cr, "stock.location", "amazon_location")
