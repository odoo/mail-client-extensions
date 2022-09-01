# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move", "duplicated_vendor_ref")

    util.create_column(cr, "account_invoice_extract_words", "ocr_selected", "boolean")
    query = """
        UPDATE account_invoice_extract_words
           SET ocr_selected = (selected_status > 0)
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_invoice_extract_words"))
    util.remove_field(cr, "account.invoice_extract.words", "selected_status")

    util.create_column(cr, "account_move", "extract_attachment_id", "int4")
    query = """
        UPDATE account_move
           SET extract_attachment_id = message_main_attachment_id
         WHERE message_main_attachment_id IS NOT NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move"))
