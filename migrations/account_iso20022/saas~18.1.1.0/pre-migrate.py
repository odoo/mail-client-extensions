from odoo.upgrade import util


def migrate(cr, version):
    # Move the `iso20022_charge_bearer` from `account.batch.payment` to the `account.payment`s it contains.
    util.create_column(cr, "account_payment", "iso20022_charge_bearer", "varchar")
    util.create_column(cr, "account_journal", "iso20022_charge_bearer", "varchar", default="SHAR")
    util.explode_execute(
        cr,
        """
        UPDATE account_payment AS ap
           SET iso20022_charge_bearer = abp.iso20022_charge_bearer
          FROM account_batch_payment AS abp
         WHERE ap.batch_payment_id = abp.id
        """,
        table="account_payment",
        alias="ap",
    )
    util.remove_field(cr, "account.batch.payment", "iso20022_charge_bearer")
