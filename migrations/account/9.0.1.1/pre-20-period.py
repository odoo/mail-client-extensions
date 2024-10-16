from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    The concept of period does not exist anymore, instead write last period date on date field on model
    """

    # Do the same for account_move
    query = """
        UPDATE account_move a
           SET date = p.date_stop
          FROM account_period p
         WHERE p.id = a.period_id
           AND ((a.date NOT BETWEEN p.date_start AND p.date_stop) OR a.date IS NULL)
           AND {parallel_filter}
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move", alias="a"))

    # Set the related date on account_move_line
    query = """
        UPDATE account_move_line aml
           SET date = am.date
          FROM account_move am
         WHERE aml.move_id = am.id
           AND {parallel_filter}
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line", alias="aml"))

    # and again on account_bank_statement
    query = """
        UPDATE account_bank_statement a
           SET date = p.date_stop
          FROM account_period p
         WHERE p.id = a.period_id
           AND ((a.date NOT BETWEEN p.date_start AND p.date_stop) OR a.date IS NULL)
           AND {parallel_filter}
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_bank_statement", alias="a"))

    # and again on account_invoice
    util.create_column(cr, "account_invoice", "date", "date")
    query = """
        UPDATE account_invoice a
           SET date = p.date_stop
          FROM account_period p
         WHERE p.id = a.period_id
           AND ((a.date_invoice NOT BETWEEN p.date_start AND p.date_stop) OR a.date_invoice IS NULL)
           AND {parallel_filter}
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_invoice", alias="a"))

    # Set the date on account_invoice related 'date_invoice' is not null
    query = """
        UPDATE account_invoice
           SET date = date_invoice
         WHERE date_invoice IS NOT NULL
           AND date IS NULL
           AND state NOT IN ('draft','cancel')
           AND {parallel_filter}
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_invoice"))
