# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "report_paperformat", "disable_shrinking", "boolean", default=False)
