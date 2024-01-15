# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sign_request", "reminder_enabled", "boolean")
    util.create_column(cr, "sign_send_request", "reminder_enabled", "boolean")
    query = """
        UPDATE sign_request
            SET reminder_enabled = true
        WHERE reminder > 0
        """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="sign_request"))
