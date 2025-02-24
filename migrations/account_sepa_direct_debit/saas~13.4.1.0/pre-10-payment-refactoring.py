from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # ===========================================================
    # Payment-pocalypse (PR: 41301 & 7019)
    # ===========================================================

    # Migrate columns/fields.

    util.remove_column(cr, "account_payment", "sdd_mandate_id")

    util.rename_field(cr, "account.move", "sdd_paying_mandate_id", "sdd_mandate_id")

    # Update existing account.move.

    util.explode_execute(
        cr,
        """
        UPDATE account_move move
           SET sdd_mandate_id = pay_backup.sdd_mandate_id
          FROM account_payment_pre_backup pay_backup
          JOIN account_payment pay
            ON pay.id = pay_backup.id
         WHERE move.id = pay.move_id
        """,
        table="account_move",
        alias="move",
    )
