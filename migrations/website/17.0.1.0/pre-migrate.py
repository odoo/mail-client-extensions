from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE website_rewrite
           SET active = 'f'
         WHERE url_to = '/'
           AND active
     RETURNING id, name
        """
    )
    if cr.rowcount:
        util.add_to_migration_reports(
            category="Website Redirects",
            message=(
                """
                    <details>
                        <summary>
                            The following redirects have been archived because, starting from Odoo 17,
                            you cannot use "/" in the "URL to". To change the homepage content,
                            use the "Homepage URL" field in the website settings or the page properties
                            on any custom page.
                        </summary>
                        <ul>%s</ul>
                    </details>
                    """
                % " ".join(
                    [
                        f"<li>{util.get_anchor_link_to_record('website.rewrite', _id, name)}</li>"
                        for _id, name in cr.fetchall()
                    ]
                )
            ),
            format="html",
        )
