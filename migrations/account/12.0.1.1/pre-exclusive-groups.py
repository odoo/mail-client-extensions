# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    inc = util.ref(cr, "account.group_show_line_subtotals_tax_included")
    exc = util.ref(cr, "account.group_show_line_subtotals_tax_excluded")
    usr = util.ref(cr, "base.group_user")
    ptl = util.ref(cr, "base.group_portal")
    pub = util.ref(cr, "base.group_public")

    env = util.env(cr)
    env.cache.invalidate()

    cr.execute(
        """
        SELECT hid
          FROM res_groups_implied_rel
         WHERE hid IN (%s, %s)
           AND gid = %s
    """,
        [inc, exc, usr],
    )

    if cr.rowcount == 1:
        [hid] = cr.fetchone()
    else:
        # either none is set, or both are set.
        # guess via ICP
        ICP = env["ir.config_parameter"]
        by_config = ICP.get_param("account.show_line_subtotals_tax_selection")
        if by_config != "tax_included":
            by_config = "tax_excluded"  # force value
        ICP.set_param("account.show_line_subtotals_tax_selection", by_config)

        hid = inc if by_config == "tax_included" else exc

    # Remove everyone from both groups, and re add them to [hid]
    cr.execute("DELETE FROM res_groups_implied_rel WHERE hid IN (%s, %s)", [inc, exc])
    cr.execute("DELETE FROM res_groups_users_rel WHERE gid IN (%s, %s)", [inc, exc])

    env["res.groups"].browse([usr, ptl, pub]).write({"implied_ids": [(4, hid)]})
