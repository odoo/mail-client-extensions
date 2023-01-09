# -*- coding: utf-8 -*-


def prepare_migration(cr):
    cr.execute(
        "SELECT res_id FROM ir_model_data WHERE module = 'account' AND name = 'group_show_line_subtotals_tax_included'"
    )
    [inc] = cr.fetchone() or [None]
    cr.execute(
        "SELECT res_id FROM ir_model_data WHERE module = 'account' AND name = 'group_show_line_subtotals_tax_excluded'"
    )
    [exc] = cr.fetchone() or [None]

    if not inc or not exc:
        # If any is unknown, we can't have users in both groups.
        # This may happen if `sale` module is uninstalled (these groups where moved from there)
        return

    cr.execute("SELECT res_id FROM ir_model_data WHERE module = 'base' AND name = 'group_user'")
    [usr] = cr.fetchone()
    cr.execute("SELECT res_id FROM ir_model_data WHERE module = 'base' AND name = 'group_portal'")
    [ptl] = cr.fetchone()
    cr.execute("SELECT res_id FROM ir_model_data WHERE module = 'base' AND name = 'group_public'")
    [pub] = cr.fetchone()

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
        cr.execute("SELECT value FROM ir_config_parameter WHERE key = 'account.show_line_subtotals_tax_selection'")
        by_config = cr.fetchone()[0] if cr.rowcount == 1 else ""
        if by_config != "tax_included":
            by_config = "tax_excluded"  # force value

        cr.execute(
            """
            INSERT
              INTO ir_config_param (key, value)
            VALUES ('account.show_line_subtotals_tax_selection', %s)
       ON CONFLICT (key)
         DO UPDATE SET value = %s
        """,
            [by_config, by_config],
        )

        hid = inc if by_config == "tax_included" else exc

    # Remove everyone from both groups, and re add them to [hid]
    cr.execute("DELETE FROM res_groups_implied_rel WHERE hid IN (%s, %s)", [inc, exc])
    cr.execute("DELETE FROM res_groups_users_rel WHERE gid IN (%s, %s)", [inc, exc])

    cr.execute(
        """
        INSERT INTO res_groups_implied_rel (hid, gid)
        VALUES (%s,%s),
               (%s,%s),
               (%s,%s)
    """,
        [hid, usr, hid, ptl, hid, pub],
    )
    cr.execute(
        """
        INSERT INTO res_groups_users_rel (gid, uid)
        SELECT %s, r.uid
          FROM res_groups_users_rel r
         WHERE r.gid IN (%s, %s, %s)
    """,
        [hid, usr, ptl, pub],
    )
