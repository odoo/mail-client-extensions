# -*- coding: utf-8 -*-
from lxml import etree, html
from lxml.html import builder as E


def carousel_indicators(element):
    for list_item in element.getchildren():
        br_element = list_item.find(".//br")
        if br_element:
            list_item.remove(br_element)


def carousel_inner(element):
    for item in element.getchildren():
        if "item" in item.classes:
            carousel_item(item)


def carousel_item(node):
    node.classes |= ["carousel-item", "oe_custom_bg", "oe_img_bg"]


def carousel_control(node):
    if "left" in node.classes:
        way, title = "prev", "Previous"
    elif "right" in node.classes:
        way, title = "next", "Next"
    else:
        return

    target = node.attrib["data-target"]
    parent = node.getparent()
    parent.remove(node)

    parent.append(
        E.DIV(
            E.CLASS("carousel-control-%s" % way),
            {"role": "img", "title": title, "data-target": target, "data-slide": way, "data-label": title},
            E.SPAN(E.CLASS("carousel-control-%s-icon" % way)),
            E.SPAN(title, E.CLASS("sr-only o_default_snippet_text")),
        )
    )


def fix_carousel(body):
    level1_modifiers = {
        "carousel-indicators": carousel_indicators,
        "carousel-inner": carousel_inner,
        "carousel-control": carousel_control,
        "item": carousel_item,
    }
    mycarouseldivs = body.xpath("//div[starts-with(@id, 'myCarousel')]|//section[starts-with(@id, 'myCarousel')]")
    for cardiv in mycarouseldivs:
        cardiv.classes |= ["s_carousel", "s_carousel_default"]
        for element in cardiv.getchildren():
            for klass in element.classes:
                level1_modifiers.get(klass, lambda n: None)(element)


def migrate(cr, version):
    utf8_parser = html.HTMLParser(encoding="utf-8")  # will allow to use `.classes` property

    cr.execute(
        """
        SELECT i.id, i.arch_db
          FROM ir_ui_view i
          JOIN website_page w ON i.id = w.view_id
         WHERE i.arch_db LIKE '%id=\"myCarousel%'
    """
    )

    for view_id, arch in cr.fetchall():
        body = html.fromstring(arch, parser=utf8_parser)
        fix_carousel(body)
        body = etree.tostring(body, encoding="unicode")
        cr.execute("UPDATE ir_ui_view SET arch_db = %s WHERE id = %s", [body, view_id])
