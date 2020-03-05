# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "quality.test_type_text", "quality.test_type_instructions")
