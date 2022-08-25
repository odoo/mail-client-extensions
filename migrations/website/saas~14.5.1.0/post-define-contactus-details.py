# -*- coding: utf-8 -*-
import re

from odoo.upgrade import util


def migrate(cr, version):
    def set_value(node, value):
        if not value:
            return node.getparent().remove(node)

        span = node.find(".//span")
        if span is not None:
            span.text = value
        else:
            node.text = value

    cr.execute("SELECT id, company_id FROM website")
    website_ids = cr.fetchall()

    if not website_ids:
        return

    pages = [
        ("/contactus", "website.contactus_page", util.ref(cr, "website.contactus_page")),
        ("/contactus-thank-you", "website.contactus_thanks", util.ref(cr, "website.contactus_thanks")),
    ]

    for website_id, company_id in website_ids:
        partner = util.env(cr)["res.company"].browse(company_id).partner_id

        for url, key, page_id in pages:
            cr.execute(
                """
                SELECT p.view_id,
                       v.key
                  FROM website_page p
                  JOIN ir_ui_view v
                    ON p.view_id = v.id
                 WHERE p.url = %s
                   AND p.website_id = %s
                """,
                [
                    url,
                    website_id,
                ],
            )
            view_id = next((vid for vid, vkey in cr.fetchall() if vkey == key), None)
            if not cr.rowcount:  # Avoid cloning the page if a specific view already exists
                util.env(cr)["website.page"].clone_page(page_id=page_id)
                # The url need to be reset to be sure it's correct. When calling the `clone_page` method,
                # the new url may be renamed to be unique (with a `-x` sufix).
                cr.execute(
                    """
                        UPDATE website_page
                            SET url = %s, header_overlay = null, is_published = 't', website_id = %s
                            WHERE id IN (SELECT max(id) FROM website_page)
                        RETURNING view_id
                    """,
                    [
                        url,
                        website_id,
                    ],
                )
                view_id = cr.fetchone()[0]

            # As we backup the contactus page before (website/saas~14.5.1.0/pre-10-contactus.py), some fresh new
            # contactus pages are created before this file execution. So it's safe to update the <li> tags content
            # according the company data, if the key is the same. Otherwise we assume this is a truly custom view.
            if not view_id:
                continue
            with util.edit_view(cr, view_id=view_id) as arch:
                nodes = arch.findall(".//li")

                set_value(nodes[0], partner.name)
                address = partner._display_address(without_company=True)
                address = re.sub(r"\n(\s|\n)*\n+", "\n", address, flags=re.MULTILINE).strip().replace("\n", "<br>")
                set_value(nodes[1], address)
                nodes[1].attrib["class"] = (nodes[1].attrib.get("class", "") + " d-flex align-items-baseline").strip()
                set_value(nodes[2], partner.phone)
                set_value(nodes[3], partner.email)
