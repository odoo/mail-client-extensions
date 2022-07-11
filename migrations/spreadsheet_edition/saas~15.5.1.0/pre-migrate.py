# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.move_model(cr, "spreadsheet.revision", "documents_spreadsheet", "spreadsheet_edition")
    util.rename_xmlid(cr, "documents_spreadsheet.spreadsheet_revision", "spreadsheet_edition.spreadsheet_revision")
    util.rename_xmlid(
        cr,
        "documents_spreadsheet.ir_config_parameter_revisions_limit_days",
        "spreadsheet_edition.ir_config_parameter_revisions_limit_days",
    )
