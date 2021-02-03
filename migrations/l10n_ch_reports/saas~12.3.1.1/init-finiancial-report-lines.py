#!/usr/bin/python


def prepare_migration(cr):
    cr.execute(
        """
            INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                 SELECT 'financial_report_line_' || lower(code),
                        'l10n_ch_reports',
                        'account.financial.html.report.line',
                        id,
                        false
                   FROM account_financial_html_report_line
                  WHERE code IN ('CHTAX_312a', 'CHTAX_312b', 'CHTAX_381a')
            ON CONFLICT DO NOTHING
        """
    )
