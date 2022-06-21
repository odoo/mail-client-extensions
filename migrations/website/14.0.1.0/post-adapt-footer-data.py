# -*- coding: utf-8 -*-
import re

from lxml import etree

from odoo.tools import html_escape

from odoo.upgrade import util


def migrate(cr, version):
    def set_value(key, value):
        nodes = tree.xpath(f".//a[starts-with(@href, '{key}:')]")
        if not nodes:
            return False

        for node in nodes:
            node.text = value
            node.attrib["href"] = f"{key}:{value}"
        return True

    xmlids = {
        "website.footer_custom": None,
        "website.template_footer_minimalist": None,
        "website.template_footer_contact": None,
        "website.template_footer_headline": None,
        "website.template_footer_descriptive": {
            "separator": "<br/>",
            "xpath": ".//div[@class='col-lg-3 offset-lg-1'].//p[@class='text-muted']",
            "node": '<p class="text-muted"><b>{company_name}</b><br/>{address}</p>',
        },
        "website.template_footer_centered": {
            "separator": " • ",
            "xpath": ".//p[@class='text-center mb-1']",
            "node": '<p class="text-center mb-1">{address}</p>',
        },
        "website.template_footer_links": {
            "separator": "<br/>",
            "xpath": ".//div[@class='col-lg-3 pb16'][last()]",
            "node": """
                <div class="col-lg-3 pb16">
                    <h5>{company_name}</h5>
                    <p class="text-muted">{address}</p>
                </div>
            """,
        },
        "website.template_footer_call_to_action": {
            "separator": " • ",
            "xpath": ".//div[@class='col-lg-9'].//p",
            "node": '<p><i class="fa fa-1x fa-fw fa-map-marker mr-2"/>{address}</p>',
        },
    }

    views_updated = []
    cr.execute("SELECT id, company_id FROM website")
    for website_id, company_id in cr.fetchall():
        partner = util.env(cr)["res.company"].browse(company_id).partner_id
        for xmlid, address_fmt in xmlids.items():
            view_id = util.ref(cr, xmlid)
            if not view_id:
                continue

            view = util.env(cr)["ir.ui.view"].browse(view_id)
            tree = etree.fromstring(view.arch_db)
            tree_updated = set_value("mailto", partner.email)
            tree_updated |= set_value("tel", partner.phone)
            if address_fmt:
                address = partner._display_address(without_company=True)
                address = (
                    re.sub(r"\n(\s|\n)*\n+", "\n", address, flags=re.MULTILINE)
                    .strip()
                    .replace("\n", address_fmt["separator"])
                )
                node = tree.find(address_fmt["xpath"])
                new_node = etree.fromstring(address_fmt["node"].format(address=address, company_name=partner.name))
                node.getparent().replace(node, new_node)
                tree_updated = True

            if not tree_updated:
                continue

            # force recreate the specific view by adding website_id in the view context
            view = view.with_context(website_id=website_id)
            view.write({"arch_db": etree.tostring(tree)})
            views_updated.append(view.name)

    if not views_updated:
        return

    util.add_to_migration_reports(
        category="Website",
        format="html",
        message=f"""
            <details>
            <summary>
                In Odoo 13.0 the footer company details are taken from the database, but in Odoo 14.0 these data are
                static and need to be customized to avoid displaying default data. These data have been set for you
                but will need to be adapted if some company details changes hapen. Here's the updated footers:
            </summary>
            <ul>{"".join("<li>{}</li>".format(html_escape(name)) for name in views_updated)}</ul>
            </details>
        """,
    )
