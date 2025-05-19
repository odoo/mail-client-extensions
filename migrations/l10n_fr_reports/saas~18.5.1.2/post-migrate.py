from odoo.upgrade import util


def migrate(cr, version):
    columns = util.get_columns(
        cr, "account_report_async_document", ignore=("id", "account_report_async_export_id", "attachment_name")
    )

    util.create_column(cr, "account_report_async_document", "_upg_export_id", "integer")

    query = """
        INSERT INTO account_report_async_document (
                    _upg_export_id,
                    account_report_async_export_id,
                    {columns}
                    )
             SELECT id,
                    max(id) over(partition by create_date),
                    {columns}
               FROM account_report_async_export
        """
    cr.execute(util.format_query(cr, query, columns=columns))

    query = """
        UPDATE ir_attachment
           SET res_field = 'attachment',
               res_model = 'account.report.async.document',
               res_id = doc.id
          FROM account_report_async_document AS doc
          JOIN account_report_async_export_ir_attachment_rel AS rel
            ON doc._upg_export_id = rel.account_report_async_export_id
         WHERE ir_attachment.id = rel.ir_attachment_id;
        """
    cr.execute(query)

    query = """
        UPDATE account_report_async_document doc
           SET attachment_name = ir_attachment.name
          FROM ir_attachment
         WHERE ir_attachment.res_id = doc.id
           AND ir_attachment.res_model = 'account.report.async.document'
           AND ir_attachment.res_field = 'attachment';
        """
    cr.execute(query)

    query = """
        SELECT _upg_export_id,
               account_report_async_export_id
          FROM account_report_async_document
         WHERE _upg_export_id <> account_report_async_export_id;
        """
    cr.execute(query)
    ids = dict(cr.fetchall())
    util.replace_record_references_batch(cr, ids, "account.report.async.export")
    cr.execute("DELETE FROM account_report_async_export WHERE id IN %s", [tuple(ids.keys())])

    util.remove_column(cr, "account_report_async_document", "_upg_export_id")

    util.remove_field(cr, "account.report.async.export", "attachment_ids")
    util.remove_field(cr, "account.report.async.export", "deposit_uid")
    util.remove_field(cr, "account.report.async.export", "declaration_uid")
    util.remove_field(cr, "account.report.async.export", "step_1_logs")
    util.remove_field(cr, "account.report.async.export", "step_2_logs")
    util.remove_field(cr, "account.report.async.export", "message")
