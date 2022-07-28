# -*- coding: utf-8 -*-

from odoo.upgrade import util


def reenable_contactus_form_values(cr):
    # The 'website_crm.contactus_form' view was a customize_show view before
    # and was kept like that by mistake during a refactoring. With this script
    # for the 16.0 version, we reenable the view for websites where users
    # disabled it, by removing the related COW'ed views.
    cr.execute(
        """
            SELECT id
              FROM ir_ui_view
             WHERE key = 'website_crm.contactus_form'
               AND website_id IS NOT NULL
               AND active = false
        """
    )
    for (vid,) in cr.fetchall():
        util.remove_view(cr, view_id=vid, key="website_crm.contactus_form")


def migrate(cr, version):
    reenable_contactus_form_values(cr)
