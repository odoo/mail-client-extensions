# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.lead", "partner_address_name")
    util.remove_field(cr, "crm.lead", "partner_address_phone")
