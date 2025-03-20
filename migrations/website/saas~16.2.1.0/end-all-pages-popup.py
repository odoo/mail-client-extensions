from lxml import etree, html

from odoo.upgrade import util

utf8_parser = html.HTMLParser(encoding="utf-8")


def get_or_create_cow_shared_blocks_view(cr, website_id):
    """
    Finds the COW shared blocks view for the given website.
    If there is no COW for this website, create it.

    :param cr: database cursor
    :param website_id: the id of the website
    :return: the id and the arch_db of the COW shared blocks view
    """
    # The new `shared_blocks` view inherits `website.layout` which might be COW
    # in the DB before the migration.
    # In such a case, since this upgrade script will be run post migration, our
    # upgrade mechanism will COW the `shared_blocks` during the upgrade as it
    # will detect this new XML view which inherit a view that is actually COWed.
    # Thus, despite being a new view created in this version, it might be COW
    # when this script is run.
    cr.execute(
        """
            SELECT id, arch_db
              FROM ir_ui_view
             WHERE key = 'website.shared_blocks'
               AND website_id = %s
             LIMIT 1
        """,
        [website_id],
    )
    if cr.rowcount > 0:
        # existing COW found
        return cr.fetchone()

    # COW the shared blocks view for the given website
    cr.execute(
        """
            SELECT id
            FROM ir_ui_view
            WHERE key = 'website.shared_blocks'
            AND website_id IS NULL
            LIMIT 1
        """
    )
    view_id = cr.fetchone()[0]

    cr.execute(
        """
            INSERT INTO ir_ui_view (priority, name, key, type, arch_fs, mode, active, customize_show, track, website_id,
                                    arch_db, inherit_id)
                SELECT priority, name, key, type, arch_fs, mode, active, customize_show, track, %(website_id)s,arch_db, (
                           -- need to find the cow parent if there is one
                           SELECT id
                             FROM ir_ui_view
                            WHERE key = 'website.layout'
                              AND (website_id IS NULL
                               OR website_id = %(website_id)s)
                         ORDER BY website_id
                            LIMIT 1
                        )
                FROM ir_ui_view
                WHERE id = %(view_id)s
            RETURNING id, arch_db
        """,
        {"website_id": website_id, "view_id": view_id},
    )
    return cr.fetchone()


def remove_and_get_popup(cr):
    """
    Removes the popup snippets from all footers.
    For active footers only, the popup content will be returned (so it can be
    later moved where it should in the shared block).

    Note that only a single footer template can be active at a time for a given
    website.

    :return: a dict of the form {
            'website_id': popups HTML content to be moved for this website
        }
    :rtype: dict
    """
    cr.execute(
        r"""
            SELECT id, arch_db, website_id, active
              FROM ir_ui_view
             WHERE arch_db->>'en_US' LIKE '%id="footer"%s\_popup%'
        """
    )
    website_popups = {}
    for view_id, arch_db, website_id, view_active in cr.fetchall():
        popups_html = {}
        for lang, arch_db_localized_str in arch_db.items():
            arch_db_localized = html.fromstring(arch_db_localized_str, parser=utf8_parser)
            popups_html_localized = ""
            for popup in arch_db_localized.xpath('.//div[@id="footer"]//div[@data-snippet="s_popup"]'):
                popups_html_localized += etree.tostring(popup, encoding="unicode")
            if view_active and popups_html_localized:
                popups_html[lang] = popups_html_localized

        with util.edit_view(cr, view_id=view_id, active=None) as arch:
            for popup in arch.xpath('.//div[@id="footer"]//div[@data-snippet="s_popup"]'):
                popup.getparent().remove(popup)

        website_popups[website_id] = popups_html

    return website_popups


def migrate(cr, version):
    """
    Deletes the popups in inactive footer views and moves the popups from the
    active footer view to the new dedicated view, considering multi-website,
    translations and COW views.

    :param cr: database cursor
    :param version: version of the module
    """
    popups_to_move = remove_and_get_popup(cr)
    for website_id, popups in popups_to_move.items():
        if not popups:
            continue

        shared_blocks_view_id, shared_blocks_view_arch = get_or_create_cow_shared_blocks_view(cr, website_id)
        shared_blocks_new_arch_db = []
        for lang, popups_html_localized in popups.items():
            # Wrap in <wrap> node before parsing to preserve external comments and
            # multi-root nodes
            new_arch = html.fromstring(
                f"<wrap>{shared_blocks_view_arch.get(lang, shared_blocks_view_arch['en_US'])}</wrap>",
                parser=utf8_parser,
            )
            new_arch.xpath('.//div[@id="o_shared_blocks"]')[0].append(
                html.fromstring(popups_html_localized, parser=utf8_parser)
            )
            new_arch = etree.tostring(new_arch, encoding="unicode")
            new_arch = new_arch.strip()[6:-7]
            shared_blocks_new_arch_db.extend([lang, new_arch])

        json_object = " || ".join(
            "jsonb_build_object(" + ", ".join("%s" for _ in chunk) + ")"
            for chunk in util.chunks(shared_blocks_new_arch_db, size=100, fmt=list)
        )

        query = util.format_query(
            cr,
            """
                UPDATE ir_ui_view
                   SET arch_db = {json_object}
                 WHERE id = %s
            """,
            json_object=util.SQLStr(json_object),
        )
        cr.execute(query, [*shared_blocks_new_arch_db, shared_blocks_view_id])
