from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """Normalize existing website_menu hierarchies for 17.0 constraints"""
    if util.version_between("17.0", "19.0"):
        # Ensure no mega menu has children. Promote its children to top-level.
        cr.execute(
            """
            UPDATE website_menu c
               SET parent_id = NULL
              FROM website_menu p
             WHERE c.parent_id = p.id
               AND p.mega_menu_content IS NOT NULL
         RETURNING c.id, c.name->>'en_US'
            """
        )
        mega_menu_children = cr.fetchall()
        if mega_menu_children:
            li = " ".join(
                "<li>{}</li>".format(
                    util.get_anchor_link_to_record("website.menu", menu_id, name or "Menu {}".format(menu_id))
                )
                for menu_id, name in mega_menu_children
            )
            util.add_to_migration_reports(
                category="Website",
                message="""
                <details>
                    <summary>
                        Some menu items were promoted to the top level because their parent
                        was a mega menu. Mega menus cannot have child menus since Odoo 17, so
                        these items were detached. Review the structure below and adjust if
                        needed.
                    </summary>
                    <ul>{}</ul>
                </details>
                """.format(li),
                format="html",
            )

        # Flatten any menu deeper than level 2: move it under the top non-megamenu ancestor
        # due to the previous update it's impossible for the top-level ancestor
        # of a non-megamenu to be a megamenu itself
        cr.execute(
            """
            WITH RECURSIVE paths AS (
                    -- start from parent-less non-mega menus
                SELECT array[id] AS path
                  FROM website_menu
                 WHERE parent_id IS NULL
                   AND mega_menu_content IS NULL

                 UNION ALL
                    -- extend paths with children
                SELECT p.path || c.id AS path
                  FROM website_menu c
                  JOIN paths p
                    ON c.parent_id = p.path[array_length(p.path, 1)]
            ) UPDATE website_menu m
                 SET parent_id = p.path[1]
                FROM paths p
               WHERE m.id = p.path[array_length(p.path, 1)]
                 AND array_length(p.path, 1) > 2
                 AND m.mega_menu_content IS NULL
           RETURNING m.id, m.name->>'en_US'
            """
        )
        flattened_menus = cr.fetchall()
        if flattened_menus:
            li = " ".join(
                "<li>{}</li>".format(
                    util.get_anchor_link_to_record("website.menu", menu_id, name or "Menu {}".format(menu_id))
                )
                for menu_id, name in flattened_menus
            )
            util.add_to_migration_reports(
                category="Website",
                message="""
                <details>
                    <summary>
                        Some menu items were moved up in the hierarchy because their depth
                        exceeded the two levels allowed starting with Odoo 17. They now sit
                        under their topmost non-mega ancestor. Review their placement below
                        and reorganize if required.
                    </summary>
                    <ul>{}</ul>
                </details>
                """.format(li),
                format="html",
            )

        # Ensure no mega menu has a parent.
        cr.execute(
            """
            UPDATE website_menu
               SET parent_id = NULL
             WHERE mega_menu_content IS NOT NULL
               AND parent_id IS NOT NULL
         RETURNING website_menu.id, website_menu.name->>'en_US'
            """
        )
        mega_menus_with_parent = cr.fetchall()
        if mega_menus_with_parent:
            li = " ".join(
                "<li>{}</li>".format(
                    util.get_anchor_link_to_record("website.menu", menu_id, name or "Menu {}".format(menu_id))
                )
                for menu_id, name in mega_menus_with_parent
            )
            util.add_to_migration_reports(
                category="Website",
                message="""
                <details>
                    <summary>
                        Mega menus can only be at the top level since Odoo 17. The following
                        menus had a parent assigned and were detached during the migration.
                        Please confirm their new placement fits your navigation layout.
                    </summary>
                    <ul>{}</ul>
                </details>
                """.format(li),
                format="html",
            )

    util.update_parent_path(cr, "website.menu", parent_field="parent_id")
