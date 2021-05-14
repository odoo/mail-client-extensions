# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "report_paperformat", "disable_shrinking", "boolean", default=False)
    util.move_field_to_module(cr, "res.partner", "country_code", "l10n_id_efaktur", "base")
