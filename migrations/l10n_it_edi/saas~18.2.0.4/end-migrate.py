from odoo.upgrade import util


def migrate(cr, version):
    query = """
        SELECT m.id
          FROM account_move AS m
          JOIN res_company AS c ON (m.company_id = c.id)
          JOIN res_country AS fiscal_cc ON (c.account_fiscal_country_id = fiscal_cc.id)
         WHERE m.state = 'posted'
           AND fiscal_cc.code = 'IT'
           AND m.l10n_it_document_type IS NULL
    """
    util.recompute_fields(cr, "account.move", ["l10n_it_document_type"], query=query)

    query = """
        SELECT m.id
          FROM account_move AS m
          JOIN res_company AS c ON (m.company_id = c.id)
          JOIN res_country AS fiscal_cc ON (c.account_fiscal_country_id = fiscal_cc.id)
         WHERE fiscal_cc.code = 'IT'
           AND (m.l10n_it_payment_method IS NULL OR m.l10n_it_payment_method = '')
    """
    util.recompute_fields(cr, "account.move", ["l10n_it_payment_method"], query=query)
