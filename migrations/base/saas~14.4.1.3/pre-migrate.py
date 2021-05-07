# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_html(cr, "res.company", "report_footer")
    util.convert_field_to_html(cr, "res.company", "report_header")
    util.convert_field_to_html(cr, "res.partner", "comment")
