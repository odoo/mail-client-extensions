from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
        UPDATE ir_attachment
           SET res_field = 'attachment',
               res_model = 'account.report.async.export',
               res_id = rel.account_report_async_export_id
          FROM account_report_async_export_ir_attachment_rel AS rel
         WHERE ir_attachment.id = rel.ir_attachment_id;
    """)

    util.create_column(cr, "account_report_async_export", "attachment_name", "varchar", default="report")

    cr.execute("""
        UPDATE account_report_async_export export
           SET attachment_name = ir_attachment.name
          FROM account_report_async_export_ir_attachment_rel AS rel
          JOIN ir_attachment
            ON ir_attachment.id = rel.ir_attachment_id
         WHERE rel.account_report_async_export_id = export.id;
    """)

    util.remove_field(cr, "account.report.async.export", "attachment_ids")
