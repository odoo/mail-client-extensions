# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "account.move", "type", "move_type")
    util.rename_field(cr, "account.invoice.report", "type", "move_type")
    util.rename_field(cr, "account.move.line", "tag_ids", "tax_tag_ids")

    incoterm_codes = "DAF,DES,DEQ,DDU,DAT".split(",")

    for code in incoterm_codes:
        util.force_noupdate(cr, "account.incoterm_%s" % code)

    cr.execute(
        """
        UPDATE account_incoterms
        set active = 'f'
        where id in %s
    """,
        [tuple(util.ref(cr, "account.incoterm_%s" % code) for code in incoterm_codes)],
    )

    util.remove_field(cr, 'account.payment', 'destination_journal_id')
    util.create_column(cr, 'account_payment', 'is_internal_transfer', 'boolean')
    cr.execute("""
    UPDATE account_payment
       SET is_internal_transfer = (payment_type = 'transfer')
    """)
    # change payment_type from 'transfer' to 'inbound', update partner_id & move_name
    cr.execute("""
    UPDATE account_payment pay
       SET payment_type = 'outbound',
           partner_id = comp.partner_id,
           move_name = split_part(pay.move_name, '§§', 1)
      FROM account_journal journal
      JOIN res_company comp ON comp.id = journal.company_id
     WHERE journal.id = pay.journal_id
       AND pay.payment_type = 'transfer'
    """)
