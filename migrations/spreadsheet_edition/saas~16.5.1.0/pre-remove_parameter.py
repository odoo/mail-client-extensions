# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "spreadsheet_edition.ir_config_parameter_revisions_limit_days")
