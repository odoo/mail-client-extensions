# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    records_to_update_xmlid = [
        "internal_knowledge",
        "internal_template",
        "finance_status",
        "finance_fiscal_year",
        "marketing_assets",
        "finance_status_inbox",
        "finance_status_tc",
        "finance_status_validated",
        "finance_documents_bill",
        "finance_documents_expense",
        "finance_documents_vat",
        "finance_documents_fiscal",
        "finance_documents_financial",
        "finance_documents_Contracts",
        "marketing_assets_ads",
        "marketing_assets_brochures",
        "marketing_assets_images",
        "marketing_assets_Videos",
    ]
    for record in records_to_update_xmlid:
        util.if_unchanged(cr, f"documents.documents_{record}", util.update_record_from_xml)
