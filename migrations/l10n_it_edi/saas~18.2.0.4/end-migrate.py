from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
        SELECT m.id
          FROM account_move AS m
          JOIN res_company AS c ON (m.company_id = c.id)
          JOIN res_country AS fiscal_cc ON (c.account_fiscal_country_id = fiscal_cc.id)
         WHERE m.state = 'posted'
           AND fiscal_cc.code = 'IT'
           AND m.l10n_it_document_type IS NULL
    """)
    move_ids_posted_wo_itdoctype = [r[0] for r in cr.fetchall()]
    util.recompute_fields(
        cr,
        "account.move",
        ["l10n_it_document_type"],
        ids=move_ids_posted_wo_itdoctype,
    )

    cr.execute("""
        SELECT m.id
          FROM account_move AS m
          JOIN res_company AS c ON (m.company_id = c.id)
          JOIN res_country AS fiscal_cc ON (c.account_fiscal_country_id = fiscal_cc.id)
         WHERE fiscal_cc.code = 'IT'
           AND (m.l10n_it_payment_method IS NULL OR m.l10n_it_payment_method = '')
    """)
    move_ids_wo_itpaymethod = [r[0] for r in cr.fetchall()]
    util.recompute_fields(
        cr,
        "account.move",
        ["l10n_it_payment_method"],
        ids=move_ids_wo_itpaymethod,
    )
