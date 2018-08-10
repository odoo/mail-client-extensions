# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""SELECT id, report_type FROM account_account_type""")
    res = cr.dictfetchall()

    tables = ['account_account', 'account_account_template']

    for old_type in res:
        old_type['new_type'] = ''
        if old_type['report_type'] == 'income':
            old_type['new_type'] = util.ref(cr, 'account.data_account_type_revenue')
        if old_type['report_type'] == 'expense':
            old_type['new_type'] = util.ref(cr, 'account.data_account_type_expenses')
        if old_type['report_type'] == 'asset':
            old_type['new_type'] = util.ref(cr, 'account.data_account_type_current_assets')
        if old_type['report_type'] == 'liability':
            old_type['new_type'] = util.ref(cr, 'account.data_account_type_current_liabilities')
        if old_type['id'] in [util.ref(cr, 'account.data_account_type_bank'), util.ref(cr, 'account.data_account_type_cash')]:
            old_type['new_type'] = util.ref(cr, 'account.data_account_type_liquidity')

        if old_type['new_type']:
            for table in tables:
                cr.execute("""UPDATE %s
                            SET user_type_id = %s
                            WHERE user_type_id = %s
                            """ % (table, old_type['new_type'], old_type['id']))

    for table in tables:
        cr.execute("""UPDATE %s
            SET user_type_id = %s
            WHERE type = 'receivable'
            """ % (table, util.ref(cr, 'account.data_account_type_receivable')))

        cr.execute("""UPDATE %s
            SET user_type_id = %s
            WHERE type = 'payable'
            """ % (table, util.ref(cr, 'account.data_account_type_payable')))

        cr.execute("""UPDATE %s
            SET user_type_id = %s
            WHERE type = 'liquidity'
            """ % (table, util.ref(cr, 'account.data_account_type_liquidity')))

    types_to_keep = [
        util.ref(cr, 'account.data_account_type_receivable'),
        util.ref(cr, 'account.data_account_type_payable'),
        util.ref(cr, 'account.data_account_type_liquidity'),
        util.ref(cr, 'account.data_account_type_current_assets'),
        util.ref(cr, 'account.data_account_type_non_current_assets'),
        util.ref(cr, 'account.data_account_type_prepayments'),
        util.ref(cr, 'account.data_account_type_fixed_assets'),
        util.ref(cr, 'account.data_account_type_current_liabilities'),
        util.ref(cr, 'account.data_account_type_non_current_liabilities'),
        util.ref(cr, 'account.data_account_type_equity'),
        util.ref(cr, 'account.data_unaffected_earnings'),
        util.ref(cr, 'account.data_account_type_other_income'),
        util.ref(cr, 'account.data_account_type_revenue'),
        util.ref(cr, 'account.data_account_type_depreciation'),
        util.ref(cr, 'account.data_account_type_expenses'),
        util.ref(cr, 'account.data_account_type_direct_costs'),
    ]

    for table in tables:
        cr.execute("""UPDATE %s
            SET user_type_id = %s
            WHERE user_type_id NOT IN %s
            """ % (table, util.ref(cr, 'account.data_account_type_current_assets'), tuple(types_to_keep)))

    cr.execute("""DELETE FROM account_account_type
        WHERE id NOT IN %s
        """, (tuple(types_to_keep),))
    cr.execute("""DELETE FROM ir_model_data
        WHERE
            res_id NOT IN %s
            AND model = 'account.account.type'
        """, (tuple(types_to_keep),))

    # compute related field on account_move_line
    cr.execute("alter table account_move_line drop constraint account_move_line_user_type_id_fkey")
    cr.execute("drop index account_move_line_user_type_id_index")
    cr.execute("""
        UPDATE account_move_line aml
           SET user_type_id = acc.user_type_id
          FROM account_account acc
         WHERE aml.account_id = acc.id
    """)
    cr.execute("create index account_move_line_user_type_id_index on account_move_line (user_type_id)")
    cr.execute("alter table account_move_line add constraint account_move_line_user_type_id_fkey FOREIGN KEY (user_type_id) REFERENCES account_account_type(id) ON DELETE SET NULL")

    """
        Compute related field internal_type
    """
    cr.execute("""UPDATE account_account
        SET internal_type = t.type
        FROM account_account_type t
        WHERE t.id = user_type_id
        """)
