# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.convert_binary_field_to_attachment(cr, "sdd.mandate", "original_doc")
