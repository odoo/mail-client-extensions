from odoo.upgrade import util


def migrate(cr, version):
    updated = {}
    while True:
        cr.execute("""
        WITH dups AS (
            SELECT unnest(array_agg(id)) as id
                FROM website_controller_page
            GROUP BY page_type, name_slugified
            HAVING count(id) > 1
        )
        UPDATE website_controller_page p
            SET name_slugified = concat(p.name_slugified, '-', p.id)
            FROM dups
            WHERE dups.id = p.id
        RETURNING p.id, p.page_name
        """)
        if not cr.rowcount:
            break
        for _id, page_name in cr.fetchall():
            updated[_id] = {"name": page_name}

    if updated:
        query = """
            UPDATE website_menu m
               SET url = concat('/model/', p.name_slugified)
              FROM website_controller_page p
             WHERE p.id = m.controller_page_id
               AND p.id IN %s
        """
        cr.execute(query, [tuple(updated)])

        msg = """
        <details>
            <summary>
                <p>The URLs of the following records have been changed.</p>
                <p>Please check that they are still meaningful to the end user.</p>
            </summary>
            <ul>{}</ul>
        </details>
        """.format(
            " ".join(
                [
                    f"<li>{util.get_anchor_link_to_record('website.controller.page', _id, vals['name'])}</li>"
                    for _id, vals in updated.items()
                ]
            )
        )
        util.add_to_migration_reports(msg, category="Website", format="html")

    cr.execute("ALTER TABLE website_controller_page RENAME COLUMN page_name TO name")
    util.remove_field(cr, "website.controller.page", "page_name")
