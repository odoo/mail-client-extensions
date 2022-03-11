# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "helpdesk_ticket", "analytic_account_id", "int4")
    query = """
        UPDATE helpdesk_ticket ht
            SET analytic_account_id = p.analytic_account_id
          FROM project_project p
         WHERE p.id = ht.project_id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="helpdesk_ticket", alias="ht"))
