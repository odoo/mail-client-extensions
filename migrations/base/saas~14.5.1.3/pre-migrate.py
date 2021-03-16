# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "company_details", "text")
    util.create_column(cr, "res_company", "layout_background", "character varying", default="Blank")
