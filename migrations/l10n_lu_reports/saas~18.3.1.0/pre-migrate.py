from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
        UPDATE ir_attachment
           SET res_field = 'attachment_bin',
                res_model = 'l10n_lu.stored.intra.report',
                res_id = l10n_lu_stored_intra_report.id
          FROM l10n_lu_stored_intra_report
         WHERE ir_attachment.id = l10n_lu_stored_intra_report.attachment_id;
    """)

    util.create_column(cr, "l10n_lu_stored_intra_report", "name", "varchar", default="report")

    cr.execute("""
        UPDATE l10n_lu_stored_intra_report
           SET name = ir_attachment.name
          FROM ir_attachment
         WHERE l10n_lu_stored_intra_report.attachment_id = ir_attachment.id;
    """)

    util.remove_field(cr, "l10n_lu.stored.intra.report", "attachment_id")
