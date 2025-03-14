import odoo.upgrade.util.snippets as snip


def remove_data_snippet_and_name(el):
    if el.get("data-snippet"):
        el.attrib.pop("data-snippet")
    if el.get("data-name"):
        el.attrib.pop("data-name")
    return True


def migrate(cr, version):
    """
    Delete the "data-snippet" and "data-name" attributes on background images
    that appeared at the change of parallax.

    :param cr: database cursor.
    :param version: version of the module.
    """
    snip.convert_html_content(
        cr,
        snip.html_converter(
            remove_data_snippet_and_name, selector="//*[hasclass('s_parallax_bg')][@data-snippet or @data-name]"
        ),
        where_column=r"~ '\ys_parallax_bg\y'",
    )
