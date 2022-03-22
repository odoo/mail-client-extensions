# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "base_vat.company_form_vat")
    util.remove_view(cr, "base_vat.view_partner_form")
