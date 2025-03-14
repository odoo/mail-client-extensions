from odoo.upgrade import util

UUID_RECOMPUTATION_CRON_CODE = """
env.cr.execute('''
    SELECT to_update.move_id
    FROM
    (
        SELECT move.id AS move_id, move.date AS move_date
        FROM account_edi_document doc
        JOIN account_move move ON move.id = doc.move_id
        JOIN res_company ON res_company.id = move.company_id
        JOIN res_country ON res_country.id = res_company.account_fiscal_country_id
        WHERE doc.edi_format_id = %(cfdi_format)s
        AND doc.state = 'sent'
        AND move.l10n_mx_edi_cfdi_uuid IS NULL
        AND res_country.code = 'MX'

        UNION

        SELECT move.id AS move_id, move.date AS move_date
        FROM account_move move
        JOIN ir_attachment ON move.id = ir_attachment.res_id AND ir_attachment.res_model = 'account.move'
        JOIN res_company ON res_company.id = move.company_id
        JOIN res_country ON res_country.id = res_company.account_fiscal_country_id
        WHERE move.state = 'posted'
        AND move.move_type IN ('in_invoice', 'in_refund')
        AND move.l10n_mx_edi_cfdi_uuid IS NULL
        AND ir_attachment.mimetype = 'application/xml'
        AND res_country.code = 'MX'
    ) to_update
    ORDER BY to_update.move_date DESC
    LIMIT 1000
''', {
    'cfdi_format': env.ref('l10n_mx_edi.edi_cfdi_3_3').id,
})

move_ids = [move_id for (move_id,) in env.cr.fetchall()]
env['account.move'].browse(move_ids)._compute_l10n_mx_edi_cfdi_uuid()
"""


def migrate(cr, version):
    util.create_cron(
        cr, "l10n_mx_edi: recompute UUID", "account.move", UUID_RECOMPUTATION_CRON_CODE, interval=(20, "minutes")
    )
