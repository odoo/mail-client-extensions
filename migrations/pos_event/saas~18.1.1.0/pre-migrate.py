from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE event_registration r
           SET sale_status = 'cancel'
          FROM pos_order_line l
          JOIN pos_order o
            ON o.id = l.order_id
         WHERE l.id = r.pos_order_line_id
           AND o.state = 'cancel'
        """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="event_registration", alias="r"))

    cr.execute(
        """
        UPDATE event_registration r
           SET sale_status = CASE WHEN round(o.amount_total, cr.decimal_places) = 0 THEN 'free' ELSE 'sold' END
          FROM pos_order_line l
          JOIN pos_order o
            ON o.id = l.order_id
          JOIN pos_session s
            ON s.id = o.session_id
          JOIN pos_config c
            ON c.id = s.config_id
          JOIN account_journal j
            ON j.id = c.journal_id
          JOIN res_currency cr
            ON cr.id = j.currency_id
         WHERE l.id = r.pos_order_line_id
           AND o.state <> 'cancel'
        """
    )
