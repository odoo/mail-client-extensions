# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
import logging

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.account.saas-12.4." + __name__)


def migrate(cr, version):

    idx_list = [
        ("_mig124_ai_currency_id", "account_invoice", "currency_id"),
        ("_mig124_il_name", "account_invoice_line", "name"),
        ("_mig124_il_invoice_id", "account_invoice_line", "invoice_id"),
        ("_mig124_il_account_id", "account_invoice_line", "account_id"),
        ("_mig124_ml_name", "account_move_line", "name"),
        ("_mig124_ml_account_id", "account_move_line", "account_id"),
    ]

    # indexes will be dropped at end-10-account-pocalypse.py
    create_index_queries = []
    util.ENVIRON["__created_accounting_idx"] = []
    for index_name, table_name, column_name in idx_list:
        util.ENVIRON["__created_accounting_idx"].append(index_name)
        create_index_queries.append("CREATE INDEX %s ON %s(%s)" % (index_name, table_name, column_name))
    _logger.info("creating %s indexes (might be slow)", len(create_index_queries))
    util.parallel_execute(cr, create_index_queries)
