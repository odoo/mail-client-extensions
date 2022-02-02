# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_expense", "state_processed", "boolean")
    query = "UPDATE hr_expense SET state_processed = (extract_state = 'waiting_extraction')"
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="hr_expense"))
