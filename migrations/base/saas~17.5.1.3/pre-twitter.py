from odoo.upgrade import util
from odoo.upgrade.util import snippets


def remove_s_twitter(el):
    el.getparent().remove(el)
    return True


def migrate(cr, version):
    if util.module_installed(cr, "website_twitter"):
        # Remove all twitter snippets that were added by users
        snippets.convert_html_content(
            cr,
            snippets.html_converter(remove_s_twitter, selector="//*[@data-snippet='s_twitter']"),
            where_column=r"LIKE '%data-snippet=_s\_twitter%'",
        )

    if util.module_installed(cr, "website_event_twitter_wall"):
        # Remove event menus that would lead to a 404.
        cr.execute(
            """
            DELETE FROM website_menu m
                  USING website_event_menu e
                  WHERE e.menu_id = m.id
                    AND e.menu_type = 'social'
                    AND m.url LIKE '/event/%/social'
            """
        )

    # Remove twitter apps
    util.remove_module(cr, "website_event_twitter_wall")
    util.remove_module(cr, "website_twitter_wall")
    util.remove_module(cr, "website_twitter")
