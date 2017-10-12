# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'res_company', 'tax_exigibility', 'boolean')
    cr.execute("""
        UPDATE res_company c
           SET tax_exigibility = EXISTS(SELECT 1
                                          FROM account_tax t
                                         WHERE t.company_id = c.id
                                           AND tax_exigibility = 'on_payment')
    """)

    util.create_column(cr, 'res_company', 'account_opening_move_id', 'int4')
    for f in 'company_data_done bank_data_done fy_data_done coa_done bar_closed'.split():
        util.create_column(cr, 'res_company', 'account_setup_' + f, 'boolean')

    cr.execute("""
        UPDATE res_company c
           SET account_setup_company_data_done = (name != 'My Company' or
                                                  email != 'info@yourcompany.com' or
                                                  phone IS NOT NULL or
                                                  EXISTS(SELECT 1 FROM ir_attachment
                                                          WHERE res_id = c.id
                                                            AND res_model = 'res.company'
                                                            AND res_field = 'image'
                                                            AND type='binary')),
               account_setup_bank_data_done = EXISTS(SELECT 1 FROM account_journal WHERE company_id=c.id),
               account_setup_fy_data_done = (fiscalyear_last_month BETWEEN 1 AND 12 AND
                                             fiscalyear_last_day BETWEEN 1 AND 31) IS TRUE,
               account_setup_coa_done = EXISTS(SELECT 1 FROM account_account WHERE company_id=c.id),
               account_setup_bar_closed = false
    """)
