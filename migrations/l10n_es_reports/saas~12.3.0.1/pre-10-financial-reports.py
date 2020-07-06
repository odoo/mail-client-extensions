# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Records with XML ids mod_347_operations_real_estates_bought and mod_347_operations_regular_sold
    # were swapped in 12.0
    cr.execute(
        """
        UPDATE ir_model_data
           SET res_id = (
               SELECT id
                 FROM account_financial_html_report_line
                WHERE code = 'aeat_' || ir_model_data.name
           )
         WHERE name IN ('mod_347_operations_regular_bought', 'mod_347_operations_regular_sold')
    """
    )
