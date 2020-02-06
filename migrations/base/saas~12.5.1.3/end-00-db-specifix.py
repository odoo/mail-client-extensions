# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def _openerp(cr, version):
    cr.execute(
        """
        UPDATE pos_payment_method
           SET receivable_account_id = 7792
         WHERE company_id = 1
    """
    )
    cr.execute(
        """
        UPDATE event_event
           SET cover_properties = REPLACE(REPLACE(cover_properties,
                                                  'cover_mid',
                                                  'o_half_screen_height o_record_has_cover'),
                                          '"background-image": "none"',
                                          '"background-image": "' || custom_banner_url || '"')
    """
    )
    cr.execute(
        """
        UPDATE ir_ui_view
           SET active = false
         WHERE id IN (SELECT res_id
                        FROM ir_model_data
                       WHERE model = 'ir.ui.view'
                         AND module IN ('website_event', 'website_blog')
                         AND name IN ('opt_index_sidebar', 'opt_blog_post_sidebar',
                                      'view_blog_post_list', 'opt_posts_loop_show_teaser')
                     )
    """
    )
    cr.execute(
        """
        UPDATE ir_ui_view
           SET active = true
         WHERE id IN (SELECT res_id
                        FROM ir_model_data
                       WHERE model = 'ir.ui.view'
                         AND module IN ('website_event', 'website_blog')
                         AND name = 'opt_posts_loop_show_cover'
                     )
    """
    )


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {"8851207e-1ff9-11e0-a147-001cc0f2115e": _openerp})
