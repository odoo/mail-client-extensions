# -*- coding: utf-8 -*-
import re
from lxml import etree

parser = etree.XMLParser()


def migrate(cr, version):
    # Select all customized headers and add the 'oe_structure_solo' class that
    # early 14.0 users will not have received.
    hasclass = "contains(concat(' ', normalize-space(@class), ' '), ' {} ')".format
    xpath = f"//*[{hasclass('oe_structure')}][contains(@id, 'oe_structure')]"
    xpath += f"[not({hasclass('oe_structure_multi')})]"
    xpath += f"[not({hasclass('oe_structure_solo')})]"
    header_template_keys = (
        "website.template_header_default",
        "website.template_header_default_oe_structure_header_default_1",
        "website.template_header_default_align_center",
        "website.template_header_default_align_right",
        "website.template_header_hamburger",
        "website.template_header_hamburger_oe_structure_header_hamburger_1",
        "website.template_header_hamburger_oe_structure_header_hamburger_2",
        "website.template_header_hamburger_oe_structure_header_hamburger_3",
        "website.template_header_hamburger_align_center",
        "website.template_header_hamburger_align_right",
        "website.template_header_vertical",
        "website.template_header_vertical_oe_structure_header_vertical_1",
        "website.template_header_vertical_oe_structure_header_vertical_2",
        "website.template_header_vertical_oe_structure_header_vertical_3",
        "website.template_header_sidebar",
        "website.template_header_sidebar_oe_structure_header_sidebar_1",
        "website.template_header_slogan",
        "website.template_header_slogan_oe_structure_header_slogan_1",
        "website.template_header_slogan_oe_structure_header_slogan_2",
        "website.template_header_slogan_oe_structure_header_slogan_3",
        "website.template_header_contact",
        "website.template_header_contact_oe_structure_header_contact_1",
        "website.template_header_minimalist",
        "website.template_header_boxed",
        "website.template_header_boxed_oe_structure_header_boxed_1",
        "website.template_header_boxed_oe_structure_header_boxed_2",
        "website.template_header_centered_logo",
        "website.template_header_image",
        "website.template_header_image_oe_structure_header_image_1",
        "website.template_header_image_oe_structure_header_image_2",
        "website.template_header_hamburger_full",
        "website.template_header_hamburger_full_oe_structure_header_hamburger_full_1",
        "website.template_header_magazine",
        "website.template_header_magazine_oe_structure_header_magazine_1",
    )
    cr.execute(
        """
            SELECT id, arch_db
              FROM ir_ui_view
             WHERE key in %s
               AND website_id IS NOT NULL
        """,
        (header_template_keys,),
    )
    for view_id, arch_db in cr.fetchall():
        arch_db = re.sub(r"^<\?xml .+\?>\s*", "", arch_db.strip())
        # Wrap in <wrap> node before parsing to preserve external comments (and
        # maybe multi-root nodes ?)
        tree = etree.fromstring(f"<wrap>{arch_db}</wrap>", parser=parser)

        oe_structure_nodes = tree.xpath(xpath)
        if not oe_structure_nodes:
            continue
        for node in oe_structure_nodes:
            node.attrib["class"] += " oe_structure_solo"
        arch_db = etree.tostring(tree, encoding="unicode")
        arch_db = re.sub(r"(^<wrap>|</wrap>$)", "", arch_db.strip())

        cr.execute("UPDATE ir_ui_view SET arch_db = %s WHERE id = %s", (arch_db, view_id))
