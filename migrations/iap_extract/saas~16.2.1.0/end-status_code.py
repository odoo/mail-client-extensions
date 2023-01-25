# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "extract.mixin", "extract_status_code")


def migrate_status_code(cr, model_name):
    table = util.table_of_model(cr, model_name)

    util.create_column(cr, table, "extract_status", "varchar")
    status_code_mapping = {
        0: "success",
        1: "processing",
        2: "error_internal",
        3: "error_no_credit",
        4: "error_document_not_found",
        5: "error_no_document_name",
        6: "error_unsupported_format",
        7: "error_file_names_not_matching",
        8: "error_no_connection",
        9: "error_maintenance",
        10: "error_password_protected",
        11: "error_too_many_pages",
        12: "error_invalid_account_token",
        14: "error_unsupported_size",
        15: "error_no_page_count",
        16: "error_pdf_conversion_to_images",
    }

    queries = []
    for status_code, status in status_code_mapping.items():
        query = cr.mogrify(
            """
                UPDATE {table}
                   SET extract_status = %s
                 WHERE extract_status_code = %s
            """.format(
                table=table
            ),
            [status, status_code],
        ).decode()
        queries.extend(
            util.explode_query_range(
                cr,
                query,
                table=table,
            )
        )
    util.parallel_execute(cr, queries)

    util.remove_field(cr, model_name, "extract_status_code")
