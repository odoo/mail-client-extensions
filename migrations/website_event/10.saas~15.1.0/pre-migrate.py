# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'event.event', 'show_menu', 'website_menu')

    util.rename_xmlid(cr, 'website_event.view_event_sale_form',
                      'website_event.event_event_view_form_inherit_website')
    util.force_noupdate(cr, 'website_event.event_event_view_form_inherit_website', False)
