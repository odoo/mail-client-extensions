# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.country", "street_format")
    util.remove_field(cr, "res.company", "street_name")
    util.remove_field(cr, "res.company", "street_number")
    util.remove_field(cr, "res.company", "street_number2")

    util.remove_view(cr, "base_address_extended.view_res_company_extended_form")
    util.remove_view(cr, "base_address_extended.view_partner_address_structured_form")
    util.remove_view(cr, "base_address_extended.view_res_country_extended_form")
    util.remove_view(cr, "base_address_extended.view_partner_structured_form")
