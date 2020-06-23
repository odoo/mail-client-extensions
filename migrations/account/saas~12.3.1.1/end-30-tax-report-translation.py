# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Move financial_report_lines(tax report only) translation to account_tax_report_line
    cr.execute(
        """
            UPDATE ir_translation
               SET res_id = atrl.id,
                   name = 'account.tax.report.line,name'
              FROM financial_report_lines_v12_bckp frl_v12
              JOIN account_tax_report_line atrl ON REPLACE(atrl.name, ' ', '') = REPLACE(frl_v12.name, ' ', '')
             WHERE frl_v12.id = ir_translation.res_id AND ir_translation.type = 'model'
               AND ir_translation.name = 'account.financial.html.report.line,name'
        """
    )
