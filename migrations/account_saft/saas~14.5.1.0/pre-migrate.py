# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===============================================================
    # Tax details per move line (PR:70866 & PR:18344)
    # ===============================================================

    for template_name in (
        "SaftTemplate",
        "GeneralLedgerEntriesTemplate",
        "MasterFilesTemplate",
        "HeaderTemplate",
        "TaxInformationStructure",
        "CustomerSupplierTemplate",
        "AmountStructureTemplate",
        "BalanceStructureTemplate",
        "CompanyHeaderStructureTemplate",
        "BankAccountTemplate",
        "ContactHeaderStructureTemplate",
        "AddressStructureTemplate",
    ):
        util.remove_view(cr, f"account_saft.{template_name}")
