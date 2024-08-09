from odoo.upgrade.util import snippets


def replace_z_index_classes(el):
    zindex_classes = {"z-index-0": "z-0", "z-index-1": "z-1"}

    for old_utility, new_utility in zindex_classes.items():
        if old_utility in el.classes:
            el.classes -= [old_utility]
            el.classes |= [new_utility]


def migrate(cr, version):
    snippets.convert_html_content(
        cr,
        snippets.html_converter(
            replace_z_index_classes, selector="//*[contains(@class, 'z-index-0') or contains(@class, 'z-index-1')]"
        ),
        where_column=r"~ '\yz-index-[01]\y'",
    )
