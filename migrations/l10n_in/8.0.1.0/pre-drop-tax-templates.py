# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("""DELETE FROM account_tax_template
                        WHERE chart_template_id IN (SELECT res_id
                                                      FROM ir_model_data
                                                     WHERE module = 'l10n_in'
                                                       AND model = 'account.chart.template');
               """)
    cr.execute("""DELETE FROM ir_model_data
                        WHERE module = 'l10n_in'
                          AND model = 'account.tax.template'
               """)
