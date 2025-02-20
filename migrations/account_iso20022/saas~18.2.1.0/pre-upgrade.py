from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_journal", "iso20022_default_priority", "varchar", default="NORM")
    util.create_column(cr, "account_payment", "iso20022_priority", "varchar")
    query = """
        UPDATE account_payment p
           SET iso20022_priority = 'NORM'
          FROM account_payment_method_line l
          JOIN account_payment_method m
            ON m.id = l.payment_method_id
         WHERE l.id = p.payment_method_line_id
           AND m.code like 'iso20022%'
    """
    util.explode_execute(cr, query, table="account_payment", alias="p")
