from odoo.upgrade import util


def migrate(cr, version):
    ## Migrate for PR odoo/odoo#177234
    # controller page now are one record having an additional record_view_id
    # that is in charge of displaying one record at a time (using an url like /model/name_slugified/record-slug-45)
    # this query disables 'single' controller pages and assign the right record_view_id to the listing pages
    util.create_column(cr, "website_controller_page", "record_view_id", "integer")
    cr.execute("""
    WITH wcp_single AS (
        UPDATE website_controller_page
        SET is_published = False, record_view_id = view_id
        WHERE page_type = 'single' AND is_published = true
        RETURNING id, view_id, name_slugified
    )
    UPDATE website_controller_page AS wcp
    SET record_view_id = wcp_single.view_id
    FROM wcp_single
    WHERE wcp.name_slugified = wcp_single.name_slugified
        AND wcp.page_type = 'listing'
        AND wcp.record_view_id IS NULL
    RETURNING wcp.id, page_name
    """)

    results = cr.fetchall()
    if results:
        msg = """
        <details>
            <summary>
                <p>Single record view has been set on the following controller pages</p>
                <p>Please check that the business flows are still meaningful to the end user.</p>
            </summary>
            <ul>{}</ul>
        </details>
        """.format(
            " ".join(
                [
                    f"<li>{util.get_anchor_link_to_record('website.controller.page', _id, name)}</li>"
                    for _id, name in results
                ]
            )
        )
        util.add_to_migration_reports(msg, category="Website", format="html")

    # Report the pages that don't have a view for single records
    cr.execute("""
        SELECT id, page_name, name_slugified
          FROM website_controller_page
         WHERE record_view_id IS NULL
    """)
    listing_no_record = cr.fetchall()
    if listing_no_record:
        msg = """
        <details>
            <summary>
                <p>The following endpoints are not able to display single records</p>
                <p>Please check that the business flows are still meaningful to the end user.</p>
            </summary>
            <ul>{}</ul>
        </details>
        """.format(
            " ".join(
                [
                    f"<li>{util.get_anchor_link_to_record('website.controller.page', _id, '{} (/model/{})'.format(name, name_slugified))}</li>"
                    for _id, name, name_slugified in listing_no_record
                ]
            )
        )
        util.add_to_migration_reports(msg, category="Website", format="html")

    # Report the pages that have no listing
    cr.execute("""
        SELECT id, page_name, name_slugified
          FROM website_controller_page
         WHERE record_view_id = view_id
    """)
    only_record = cr.fetchall()
    if only_record:
        msg = """
        <details>
            <summary>
                <p>The following records are set to only display single records, they may not be relevant anymore and have been unpublished.</p>
                <p>Please check that the business flows are still meaningful to the end user.</p>
            </summary>
            <ul>{}</ul>
        </details>
        """.format(
            " ".join(
                [
                    f"<li>{util.get_anchor_link_to_record('website.controller.page', _id, '{} (/model/{})'.format(name, name_slugified))}</li>"
                    for _id, name, name_slugified in only_record
                ]
            )
        )
        util.add_to_migration_reports(msg, category="Website", format="html")

    util.remove_field(cr, "website.controller.page", "page_type")
