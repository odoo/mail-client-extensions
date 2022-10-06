# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # cr.execute("DROP TABLE account_invoice CASCADE")
    # cr.execute("DROP TABLE account_invoice_line CASCADE")
    # cr.execute("DROP TABLE account_invoice_tax CASCADE")
    # cr.execute("DROP TABLE IF EXISTS invl_aml_mapping CASCADE")
    cr.execute("DROP TABLE IF EXISTS account_voucher CASCADE")
    cr.execute("DROP TABLE IF EXISTS account_voucher_line CASCADE")
    cr.execute("DROP TABLE IF EXISTS am_updatable_amounts CASCADE")

    # If some Invoice/Bill have 0.000 value then it's not have payment entry so state is set as not_paid
    # So here we set state as paid for amount residual is 0.000
    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
            UPDATE account_move
               SET invoice_payment_state = 'paid'
             WHERE amount_residual = 0.000
               AND type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
               AND state = 'posted'
            """,
        ),
    )

    # If some invoice amls still have exclude_from_invoice_tab = null and amount to 0,
    # we consider they were manually added(for some reason) and set them
    # as exclude_from_invoice_tab = True. We only do that because those lines have no impact on the accounting.
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
        UPDATE account_move_line aml
           SET exclude_from_invoice_tab = true
          FROM account_move move
         WHERE move.id = aml.move_id
           AND aml.balance = 0
           AND aml.exclude_from_invoice_tab IS NULL
           AND move.type != 'entry'
            """,
            table="account_move_line",
            alias="aml",
        ),
    )

    # Other invoice amls still having exclude_from_invoice_tab=null are buggy
    cr.execute(
        """
        SELECT count(*)
          FROM account_move_line aml
          JOIN account_move move ON move.id = aml.move_id
         WHERE exclude_from_invoice_tab IS NULL
           AND move.type != 'entry'
    """
    )
    rowcount = cr.fetchone()[0]
    if rowcount > 0:
        util.add_to_migration_reports(
            f"Error, you have {rowcount} account.move.line with NULL value in exclude_from_invoice_tab field",
            "Accounting",
        )

    cr.execute(
        """
        SELECT count(*)
          FROM account_move am
          JOIN account_invoice inv ON am.id = inv.move_id
          JOIN res_currency c ON c.id=inv.currency_id
         WHERE round(am.amount_untaxed,(log(c.rounding)*-1)::int)!=round(inv.amount_untaxed,(log(c.rounding)*-1)::int)
    """
    )
    rowcount = cr.fetchone()[0]
    if rowcount > 0:
        util.add_to_migration_reports(
            f"Error, you have {rowcount} account.move with different amount_untaxed value than the account.invoice",
            "Accounting",
        )

    # clean indexes (created in pre-70-create-index.py)
    index_names = util.ENVIRON.get("__created_accounting_idx", [])
    util.parallel_execute(cr, [f'DROP INDEX IF EXISTS "{name}"' for name in index_names])
