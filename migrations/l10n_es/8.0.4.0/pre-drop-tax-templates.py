# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("""DELETE FROM account_fiscal_position_template
                        WHERE chart_template_id IN (SELECT res_id
                                                      FROM ir_model_data
                                                     WHERE module = 'l10n_es'
                                                       AND model = 'account.chart.template');
               """)
    cr.execute("""DELETE FROM account_tax_template
                        WHERE chart_template_id IN (SELECT res_id
                                                      FROM ir_model_data
                                                     WHERE module = 'l10n_es'
                                                       AND model = 'account.chart.template');
               """)
    cr.execute("""DELETE FROM ir_model_data
                        WHERE module = 'l10n_es'
                          AND model IN ('account.tax.template',
                                        'account.fiscal.position.template',
                                        'account.fiscal.position.tax.template')
               """)
