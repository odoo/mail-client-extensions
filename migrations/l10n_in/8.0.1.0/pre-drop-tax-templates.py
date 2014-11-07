# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("""DELETE FROM account_fiscal_position_tax_template
                        WHERE id IN (SELECT res_id
                                       FROM ir_model_data
                                      WHERE module = 'l10n_in'
                                        AND model = 'account.fiscal.position.tax.template');
               """)
    cr.execute("""DELETE FROM account_tax_template
                        WHERE id IN (SELECT res_id
                                       FROM ir_model_data
                                      WHERE module = 'l10n_in'
                                        AND model = 'account.tax.template');
               """)
    cr.execute("""DELETE FROM ir_model_data
                        WHERE module = 'l10n_in'
                          AND model IN ('account.tax.template', 'account.fiscal.position.tax.template');
               """)
