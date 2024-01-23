# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # move demo data
    lst = """
        demo_bank_statement_1
        demo_bank_statement_line_1
        demo_bank_statement_line_2
        demo_bank_statement_line_3
        demo_bank_statement_line_4
        demo_bank_statement_line_5

        demo_invoice_1
        demo_invoice_2
        demo_invoice_3
        demo_invoice_followup
        demo_invoice_0

        demo_invoice_january_wages
        ceo_wages_line

        demo_invoice_equipment_purchase
        coffee_machine_line

        demo_opening_move
        opening_line_1
        opening_line_2
        opening_line_3
    """

    if util.module_installed(cr, "l10n_generic_coa"):
        for xid in util.splitlines(lst):
            util.rename_xmlid(cr, "account." + xid, "l10n_generic_coa." + xid)
    else:
        # avoid deletion
        for xid in util.splitlines(lst):
            util.force_noupdate(cr, "account." + xid, noupdate=True)
