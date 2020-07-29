# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        r"""
        UPDATE ir_attachment
           SET url = '/' || url
         WHERE type='url'
           AND url ilike 'theme\_%'
           AND res_model = 'ir.module.module'
    """
    )

    cr.execute(
        """
        INSERT INTO ir_ui_view_group_rel
             SELECT id, visibility_group
               FROM ir_ui_view
              WHERE visibility_group is not null
        ON CONFLICT DO NOTHING
        """
    )
    util.remove_field(cr, "ir.ui.view", "visibility_group")

    util.update_record_from_xml(cr, "website.digest_tip_website_0")

    def rm_aboutus(*_):
        util.remove_record(cr, "website.aboutus_page")
        util.remove_view(cr, "website.aboutus")

    util.if_unchanged(cr, "website.aboutus", rm_aboutus)
    util.force_noupdate(cr, "website.aboutus")
    util.force_noupdate(cr, "website.aboutus_page")
