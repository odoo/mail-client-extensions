from odoo.upgrade import util

UUID_ORIGIN_RECOMPUTATION_CRON_CODE = """
docs = env['l10n_mx_edi.document'].search([('attachment_origin', '=', '<TO_COMPUTE>')], limit=1000)
if docs:
    docs._compute_from_attachment()
    next_date = datetime.datetime.utcnow() + datetime.timedelta(minutes=20)
    env.ref('__upgrade__.cron_post_upgrade_l10n_mx_edi_recompute_uuid_origin')._trigger(at=next_date)
"""


def migrate(cr, _version):
    util.explode_execute(
        cr,
        """
            UPDATE l10n_mx_edi_document
               SET attachment_origin = '<TO_COMPUTE>'
             WHERE l10n_mx_edi_document.attachment_id IS NOT NULL
        """,
        table="l10n_mx_edi_document",
    )

    util.create_cron(
        cr,
        "l10n_mx_edi: recompute UUID/ORIGIN",
        "l10n_mx_edi.document",
        UUID_ORIGIN_RECOMPUTATION_CRON_CODE,
        interval=(99, "days"),
    )
