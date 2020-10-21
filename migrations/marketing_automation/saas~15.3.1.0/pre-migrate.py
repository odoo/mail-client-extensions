# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Rename the field to match the one set on the <utm.source.mixin>
    util.rename_field(cr, "marketing.activity", "utm_source_id", "source_id")
