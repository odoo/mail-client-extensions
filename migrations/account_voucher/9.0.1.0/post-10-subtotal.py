# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        UPDATE account_voucher_line
           SET price_subtotal=quantity*price_unit
    """)

    cr.execute("""
        select account_voucher_line_id
        from account_tax_account_voucher_line_rel
        group by account_voucher_line_id
    """)
    ids = [i[0] for i in cr.fetchall()]
    if ids:
        util.recompute_fields(cr, "account.voucher.line", ["price_subtotal"], ids)
