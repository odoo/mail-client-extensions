from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "extract.mixin", "extract_status_code")
    util.remove_field(cr, "extract.mixin", "extract_remote_id")


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
            util.format_query(
                cr,
                """
                UPDATE {table}
                   SET extract_status = %s
                 WHERE extract_status_code = %s
                """,
                table=table,
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


def migrate_document_uuid(cr, model_name):
    table = util.table_of_model(cr, model_name)

    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            util.format_query(
                cr,
                "UPDATE {table} SET extract_remote_id = NULL WHERE extract_remote_id = -1",
                table=table,
            ),
            table=table,
        ),
    )
    util.rename_field(cr, model_name, "extract_remote_id", "extract_document_uuid")
    cr.execute(
        util.format_query(cr, "ALTER TABLE {table} ALTER COLUMN extract_document_uuid TYPE varchar", table=table)
    )
