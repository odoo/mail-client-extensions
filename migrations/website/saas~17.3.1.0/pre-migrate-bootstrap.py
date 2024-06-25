from odoo.upgrade.util import snippets


def add_alert_class(el):
    if "alert" in el.classes:
        return False
    el.classes |= ["alert"]
    return True


def fix_carousel(el):
    el.attrib["data-bs-ride"] = "true"
    el.attrib.pop("data-bs-interval")
    return True


def migrate(cr, version):
    snippets.convert_html_content(
        cr,
        snippets.html_converter(add_alert_class, selector="//*[hasclass('s_alert')]"),
        where_column=r"~ '\ys_alert\y'",
    )
    snippets.convert_html_content(
        cr,
        snippets.html_converter(fix_carousel, selector="//div[@data-bs-ride='carousel'][@data-bs-interval='0']"),
        where_column=r"~ '\ydata-bs-ride\y'",
    )
