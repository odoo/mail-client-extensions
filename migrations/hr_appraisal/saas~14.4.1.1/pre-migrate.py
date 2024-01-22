# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "request_appraisal", "lang", "varchar")
    util.convert_field_to_html(cr, "hr.appraisal.goal", "description")
