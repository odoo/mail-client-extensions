# -*- coding: utf-8 -*-
from lxml.html import builder as E

# === Carousel ===

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
    node.classes.remove("item")
    for img in node.getchildren():
        if "img-responsive" in img.classes:
            img.classes |= ["d-block"]


def carousel_control(node):
    if "left" in node.classes:
        way, title = "prev", "Previous"
        node.classes.remove("left")
    elif "right" in node.classes:
        way, title = "next", "Next"
        node.classes.remove("right")
    else:
        return

    klass = "carousel-control-%s" % way
    if "hidden" in node.classes:
        klass += " d-none"
        node.classes.remove("hidden")

    attribs = node.attrib.keys()
    if "data-target" in attribs:
        parent = node.getparent()
        parent.remove(node)
        parent.append(
            E.DIV(
                E.CLASS(klass),
                {
                    "role": "img",
                    "title": title,
                    "data-target": node.attrib["data-target"],
                    "data-slide": way,
                    "data-label": title,
                },
                E.SPAN(E.CLASS("carousel-control-%s-icon" % way)),
                E.SPAN(title, E.CLASS("sr-only o_default_snippet_text")),
            )
        )
    elif "href" in attribs:
        node.classes.remove("carousel-control")
        node.classes |= klass.split(" ")
        node.set("aria-label", title)
        node.set("title", title)


def fix_carousel(body):
    level1_modifiers = {
        "carousel-indicators": carousel_indicators,
        "carousel-inner": carousel_inner,
        "carousel-control": carousel_control,
        "item": carousel_item,
    }
    mycarouseldivs = body.xpath(
        "//div[starts-with(@id, 'myCarousel')]|//section[starts-with(@id, 'myCarousel')]"
        "|//section[hasclass('s_image_gallery')]//div[hasclass('slide')]"
    )
    for cardiv in mycarouseldivs:
        cardiv.classes |= ["s_carousel", "s_carousel_default"]
        for element in cardiv.getchildren():
            for klass in element.classes:
                level1_modifiers.get(klass, lambda n: None)(element)

# === Timeline ===

def fixli(li, nr):
    nc = []
    date = []
    icon1 = E.I(E.CLASS("fa fa-1x fa-asterisk bg-alpha rounded-circle s_timeline_icon"))
    icon2 = E.I(E.CLASS("fa fa-1x fa-asterisk bg-alpha rounded-circle s_timeline_icon"))
    content = li.xpath(".//div[hasclass('s_timeline_panel_content')]")

    for ci, cv in enumerate(content):
        nc.append(E.DIV(E.CLASS("s_timeline_content d-flex")))
        divcard = E.DIV(E.CLASS("s_card card bg-white w-100"))
        divcardbody = E.DIV(E.CLASS("card-body"))
        divcard.append(divcardbody)
        nc[ci].append(divcard)

        heading = cv.xpath(".//div[hasclass('s_timeline_heading')]")
        for h in heading:
            for el in h.getchildren():
                if "s_timeline_date" in el.classes and el.text:
                    date.append(el.text)
                else:
                    el.classes |= ["card_title"]
                    divcardbody.append(el)

        tbody = cv.xpath(".//div[hasclass('s_timeline_body')]")
        for tb in tbody:
            for el in tb.getchildren():
                el.classes |= ["card_text"]
                divcardbody.append(el)

    if not date:
        date = ["", ""]

    divdate = E.DIV(E.CLASS("s_timeline_date"),
                    E.SPAN(E.CLASS("bg-white"),
                           E.B(E.CLASS("o_default_snippet_text"),
                               date[0])))
    if ci < 1:
        nc.append(E.DIV(E.CLASS("s_timeline_content d-flex")))
    elif len(date) > 1 and date[0] != date[1]:
        divdate = E.DIV(E.CLASS("s_timeline_date"),
                        E.SPAN(E.CLASS("bg-white"),
                               E.DIV(E.I(E.CLASS("fa fa-caret-left"), style="margin: .25rem"),
                                     E.B(E.CLASS("o_default_snippet_text"),
                                         date[0]),
                                     style="white-space:nowrap; display:inline-block;")),
                        E.SPAN(E.CLASS("bg-white"),
                               E.DIV(E.B(E.CLASS("o_default_snippet_text"),
                                         date[1]),
                                     E.I(E.CLASS("fa fa-caret-right"), style="margin: .25rem"),
                                     style="white-space:nowrap; display:inline-block;")))

    nc[0].append(icon1)
    if (ci > 0):
        nc[ci].insert(0, icon2)

    nr.append(nc[0])
    nr.append(divdate)
    nr.append(nc[1])


def fix_timeline(body):
    scts = body.xpath("//section[starts-with(@class, 's_timeline')]")
    for sct in scts:
        sct.set('class', "s_timeline pt24 pb48")
        for ctn in sct.xpath("./div[hasclass('container')]"):
            ctn.classes |= ["s_timeline_line"]
            idx = sct.index(ctn)
            for rw in ctn.xpath("./div[@class='row']"):
                for divcol in rw.xpath("./div"):
                    uls = divcol.xpath("./ul[hasclass('s_timeline_ul')]")
                    for ul in uls:
                        for li in ul.xpath("./li"):
                            dc = "s_timeline_row d-flex flex-row"
                            if "s_timeline_inverted" in li.classes:
                                dc += "-reverse"
                            newrow = E.DIV(E.CLASS(dc))
                            fixli(li, newrow)
                            divcol.append(newrow)
                        divcol.remove(ul)
                    if not uls:
                        sct.insert(idx, divcol)
                        idx += 1


# Register fixers.
# Map a LIKE pattern to a fixer function
FIXERS = {
    r'%id="myCarousel%': fix_carousel,
    r'%s_image_gallery%': fix_carousel,
    r'%section class="s_timeline%': fix_timeline,
}
