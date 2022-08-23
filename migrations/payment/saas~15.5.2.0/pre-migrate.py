from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "payment_acquirer", "is_published", "boolean", default=True)
    util.rename_field(cr, "payment.acquirer", "country_ids", "available_country_ids")
    util.rename_field(cr, "payment.token", "name", "payment_details")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
                UPDATE payment_token
                   SET payment_details = RIGHT(payment_details, 4)
                 WHERE payment_details IS NOT NULL
            """,
            table="payment_token",
        ),
    )

    util.remove_field(cr, "payment.acquirer", "description")
