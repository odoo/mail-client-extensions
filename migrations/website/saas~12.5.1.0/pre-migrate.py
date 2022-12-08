# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.move_field_to_module(cr, "ir.ui.view", "track", "website_crm_score", "website")
    util.create_column(cr, "ir_ui_view", "track", "boolean")
    util.rename_field(cr, "res.config.settings", "language_count", "website_language_count")
    util.remove_field(cr, "res.config.settings", "social_googleplus")

    util.remove_field(cr, "website", "default_lang_code")
    util.remove_field(cr, "website", "social_googleplus")

    util.create_column(cr, "website_menu", "mega_menu_content", "text")
    util.create_column(cr, "website_menu", "mega_menu_classes", "varchar")

    util.rename_model(cr, "website.redirect", "website.rewrite")
    util.create_column(cr, "website_rewrite", "name", "varchar")
    util.create_column(cr, "website_rewrite", "route_id", "int4")
    cr.execute("UPDATE website_rewrite SET name = url_from")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("website.access_website_{redirect,rewrite}"), noupdate=False)
    util.rename_xmlid(cr, *eb("website.access_website_{redirect,rewrite}_designer"))

    util.rename_xmlid(cr, "website.menu_website_redirect_list", "website.menu_website_rewrite")
    util.rename_xmlid(cr, "website.view_website_redirect_search", "website.view_rewrite_search")
    util.rename_xmlid(cr, "website.website_redirect_form_view", "website.view_website_rewrite_form")
    util.rename_xmlid(cr, "website.website_redirect_tree_view", "website.action_website_rewrite_tree")
    util.rename_xmlid(cr, "website.action_website_redirect_list", "website.action_website_rewrite_list")

    for opt in {"title", "body", "button", "navbar"}:
        for cnt in range(2, 7):
            util.remove_view(cr, "website.option_font_{}_{:02}_variables".format(opt, cnt))
            cr.execute(
                """
                WITH qweb_views AS (
                    SELECT id
                       FROM ir_ui_view
                      WHERE website_id IS NOT NULL
                        AND key=%s
                        AND type='qweb'
                        AND id NOT IN (select res_id from ir_model_data where module='website' and model='ir.ui.view')
                )
                UPDATE ir_ui_view v
                    SET active='f'
                  FROM qweb_views qv
                 WHERE qv.id=v.id
               """,
                ["website.option_font_%(opt)s_0%(cnt)s_variables" % {"opt": opt, "cnt": cnt}],
            )

    # social_gooleplus is removed from the standard, but its reference is still there in views,
    # removed reference from views
    cr.execute(
        """
        SELECT id
          FROM ir_ui_view
         WHERE arch_db ilike '%website.social_googleplus%'
        """
    )

    for (view_id,) in cr.fetchall():
        with util.skippable_cm(), util.edit_view(cr, view_id=view_id) as arch:
            node = arch.find('.//a[@t-if="website.social_googleplus"]')
            if node is not None:
                node.getparent().remove(node)
