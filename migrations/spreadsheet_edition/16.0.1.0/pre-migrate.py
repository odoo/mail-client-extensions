# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.move_model(
        cr,
        "spreadsheet.revision",
        "documents_spreadsheet",
        "spreadsheet_edition",
        keep={
            "spreadsheet_revision_action",
            "spreadsheet_revision_view_search",
            "spreadsheet_revision_view_tree",
            # this one is badly named but really point to `spreadsheet.revision`
            "spreadsheet_contributor_view_form",
        },
    )

    util.rename_xmlid(
        cr,
        "documents_spreadsheet.ir_config_parameter_revisions_limit_days",
        "spreadsheet_edition.ir_config_parameter_revisions_limit_days",
    )
