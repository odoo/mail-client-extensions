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
           SET cover_properties = jsonb_set(jsonb_set(cover_properties::jsonb,
                '{background-image}', to_jsonb(custom_banner_url)),
                '{resize_class}', to_jsonb(case
                    when cover_properties::jsonb->>'resize_class' !~ '\mo_record_has_cover\M'
                      then concat('o_record_has_cover ', cover_properties::jsonb->>'resize_class')
                      else cover_properties::jsonb->>'resize_class'
                    end))
         WHERE custom_banner_url is not null
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
