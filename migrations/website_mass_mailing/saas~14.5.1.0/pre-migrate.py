# -*- coding: utf-8 -*-

import itertools

from lxml import etree, html

import odoo.upgrade.util.snippets as snip
from odoo.upgrade import util

utf8_parser = html.HTMLParser(encoding="utf-8")


def migrate(cr, version):
    for table, column in itertools.chain(snip.get_html_fields(cr), [("ir_ui_view", '"arch_db"')]):
        migrate_newsletter_popup(cr, table, column)

    util.remove_field(cr, "mailing.list", "toast_content")
    util.remove_field(cr, "mailing.list", "website_popup_ids")
    util.remove_model(cr, "website.mass_mailing.popup")
    util.remove_view(cr, "website_mass_mailing.s_newsletter_subscribe_popup_content")
    util.remove_view(cr, "website_mass_mailing.view_mail_mass_mailing_popup_form")
    util.remove_view(cr, "website_mass_mailing.mailing_list_view_form")


def migrate_newsletter_popup(cr, table, column):
    """Only an empty `<div/>` was stored inside the `ir.ui.view.arch_db`*:
    <div class="o_newsletter_popup" data-list-id="${mailing_list.id}" [...]/>
    The popup content was stored inside `website.mass_mailing.popup`
    table and retrieved in JS by RPC, based on the current website and the
    `data-list-id` attribute.

    After migration, the popup content should now have been moved directly
    inside the `ir.ui.view.arch_db`*, as it now uses the behavior of the
    regular `s_popup` and `s_newsletter_subscribe_form`.

    * or any record.HTML field."""

    # Get field that holds a newsletter popup, those should be migrated
    # (except the snippet itself)
    and_cond = "AND key != 'website_mass_mailing.s_newsletter_subscribe_popup'" if table == "ir_ui_view" else ""
    cr.execute(
        f"""
            SELECT id, {column}
              FROM {table}
             WHERE {column} LIKE '%o\\_newsletter\\_popup%'
                   {and_cond}
        """
    )
    for res_id, content in cr.fetchall():
        content = html.fromstring(content, parser=utf8_parser)
        newsletter_popup_els = content.xpath("//*[hasclass('o_newsletter_popup')]")
        for newsletter_popup_el in newsletter_popup_els:
            # Retrieve the popup content, which is stored inside a
            # `website_mass_mailing_popup` record.
            list_id = newsletter_popup_el.get("data-list-id")
            popup_content = get_popup_content(cr, list_id, res_id, table)

            # Replace the old (and empty) newsletter popup `<div/>` by the new
            # structure, and inject its popup content inside it.
            new_popup_structure = html.fromstring(
                f"""
                <div class="s_popup o_newsletter_popup o_snippet_invisible" data-name="Newsletter Popup"
                     data-vcss="001" data-invisible="1">
                    <div class="modal fade s_popup_middle o_newsletter_modal"
                         style="background-color: var(--black-50) !important;"
                         data-show-after="5000" data-display="afterDelay" data-consents-duration="7"
                         data-focus="false" data-backdrop="false" tabindex="-1" role="dialog">
                        <div class="modal-dialog d-flex">
                            <div class="modal-content oe_structure">
                                <div class="s_popup_close js_close_popup o_we_no_overlay o_not_editable"
                                     aria-label="Close">&#215;</div>
                                {popup_content}
                            </div>
                        </div>
                    </div>
                </div>""",
                parser=utf8_parser,
            )

            # `data-list-id` is now on `s_newsletter_subscribe_form`, not on
            # `o_newsletter_popup` anymore.
            new_popup_structure.xpath("//*[hasclass('s_newsletter_subscribe_form')]")[0].set("data-list-id", list_id)

            if newsletter_popup_el == content:
                # Special case: the newsletter popup snippet could be the root
                # element (eg `product.template.website_description`)
                # Note: in that case we will loop only once.
                content = new_popup_structure
            else:
                parent = newsletter_popup_el.getparent()
                parent.replace(newsletter_popup_el, new_popup_structure)

        content = etree.tostring(content, encoding="unicode")
        cr.execute(f"UPDATE {table} SET {column} = %s WHERE id = %s", [content, res_id])


def get_popup_content(cr, list_id, res_id, table):
    """Multiple case possible, most common being:
    1. ir.ui.view.arch -> most of the time, the snippet was draged & dropped,
       making the view specific, and a `website_mass_mailing_popup` related to
       that website was created.
    2. product.template.website_description -> a product may be shared between
       websites, in that case drag & dropping the snippet will create a
       `website_mass_mailing_popup` related to the website the user is editing,
       but other website will actually use that `website_mass_mailing_popup`
       even if it is not set for their website -> limitation of our previous
       system?
    3. A record could not have a `website_id` field, but have an editable HTML
       field in the frontend. In that case, it will create a
       `website_mass_mailing_popup` related to the website the user is editing,
       but other website will actually use that `website_mass_mailing_popup`
       even if it is not set for their website

    Thus, the goal is:
    - If the record has a `website_id` field:
      - If there is a `website_mass_mailing_popup` for this website
        -> We are sure this is a correct match (case 1.) -> Use that one
      - If not:
        - If there is a generic one (no website, it should never be the case
          unless created from the backend)
          -> Use that one -> Probably the correct match
        - If not:
          -> Use whichever one we find for that mailing list, even if from
             another website (case 2. described above)
    - If not (case 3.):
      -> Use whichever one we find for that mailing list, generic prefered.
         A possible case could be a record with a related, non stored
         `website_id` field.
    """

    # Get all popup content for the requested mailing list.
    cr.execute(
        """
            SELECT website_id, popup_content
              FROM website_mass_mailing_popup
             WHERE mailing_list_id = %s
        """,
        [list_id],
    )
    popups = cr.fetchall()
    popup = popups[0][1]
    # If there is only once content, use it, else, try to find the most adequate
    if len(popups) > 1:
        # A more adequate has sense only for record having a `website_id` field
        if util.column_exists(cr, table, "website_id"):
            cr.execute(f"SELECT website_id FROM {table} WHERE id = %s", [res_id])
            website_id = cr.fetchone()[0]
            popups = dict(popups)
            if website_id:
                popup = popups.get(website_id) or popups.get(None, popup)
            else:
                popup = popups.get(None, popup)

    return popup
