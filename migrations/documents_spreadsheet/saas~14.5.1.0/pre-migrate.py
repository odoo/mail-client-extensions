# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "documents_spreadsheet_folder_id", "int4")

    cr.execute(
        """
        UPDATE res_company
           SET documents_spreadsheet_folder_id=%s
    """,
        [util.ref(cr, "documents_spreadsheet.documents_spreadsheet_folder")],
    )

    util.update_record_from_xml(cr, "documents_spreadsheet.documents_spreadsheet_folder")
