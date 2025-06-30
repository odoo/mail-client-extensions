def migrate(cr, version):
    # This allows the addition of the new index account_financial_html_report_line_code_uniq
    # see odoo/enterprise@498a2d37f473e1baad35ea332e4addc558e1c906
    cr.execute(
        """
        UPDATE account_financial_html_report_line l
           SET code = 'FRTAX75'
          FROM ir_model_data d
         WHERE d.module = 'l10n_fr_reports'
           AND d.name = 'account_financial_report_line_75_fr'
           AND d.res_id = l.id
           AND l.code = 'FRTAX77'
        """
    )
