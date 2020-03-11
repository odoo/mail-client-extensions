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
