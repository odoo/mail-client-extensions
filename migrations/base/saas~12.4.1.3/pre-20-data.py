# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("base.state_mx_q{ ,_}roo"))

    cr.execute(
        "UPDATE res_lang SET date_format='%%Y-%%m-%%d' WHERE date_format='%%Y.%%m.%%d' AND id=%s",
        [util.ref(cr, "base.lang_lt")],
    )

    currencies = {"ZWD": "ZWL", "ZMK": "ZMW", "TMM": "TMT", "SRG": "SRD"}
    for old, new in currencies.items():
        cid = util.rename_xmlid(cr, "base." + old, "base." + new)
        if cid:
            cr.execute("UPDATE res_currency SET name = %s WHERE id = %s", [new, cid])

    util.delete_unused(cr, "res_currency", ["base.SDD"])

    cr.execute("UPDATE ir_ui_view SET field_parent = NULL WHERE id = %s", [util.ref(cr, "base.view_company_tree")])
