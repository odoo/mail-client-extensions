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
    # title row will never match, as (NULL = NULL) is false in SQL
    cr.execute(
        """
        UPDATE ir_ui_view v
          SET active = d.active
        FROM (          SELECT NULL "module",   NULL "name",                  NULL "active"
              UNION ALL SELECT 'website_blog',  'opt_blog_cards_design',      false
              UNION ALL SELECT 'website_blog',  'opt_blog_list_view',         false
              UNION ALL SELECT 'website_blog',  'opt_blog_post_sidebar',      false
              UNION ALL SELECT 'website_blog',  'opt_blog_sidebar_show',      false
              UNION ALL SELECT 'website_blog',  'opt_posts_loop_show_cover',  true
              UNION ALL SELECT 'website_blog',  'opt_posts_loop_show_teaser', false
              UNION ALL SELECT 'website_blog',  'view_blog_post_list',        false
              UNION ALL SELECT 'website_event', 'opt_index_sidebar',          false
             ) d
             JOIN ir_model_data md ON md.module = d.module
                                  AND md.name = d.name
        WHERE md.model = 'ir.ui.view'
          AND v.id = md.res_id
    """
    )
    cr.execute("UPDATE account_payment_term SET company_id = NULL")


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {"8851207e-1ff9-11e0-a147-001cc0f2115e": _openerp})
