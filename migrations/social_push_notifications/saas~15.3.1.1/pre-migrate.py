# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "website_visitor", "has_push_notifications", "bool")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE website_visitor
              SET has_push_notifications = TRUE
            WHERE push_token IS NOT NULL
              AND has_push_notifications = FALSE
            """,
            table="website_visitor",
        ),
    )
