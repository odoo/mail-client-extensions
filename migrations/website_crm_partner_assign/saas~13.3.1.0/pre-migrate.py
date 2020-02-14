# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # onchange -> compute + crm fields cleaning
    util.rename_field(cr, "crm.lead", "date_assign", "date_partner_assign")
