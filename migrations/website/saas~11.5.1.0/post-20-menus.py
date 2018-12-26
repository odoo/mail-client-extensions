# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # menus, step 3: use orm to recreate the same menu for the initial website,
    #                conserving the template for future use
    env = util.env(cr)
    main_website = env['website'].search([], limit=1, order='id asc')
    # some faulty menus might have been created during the upgrade
    # during loading of website_data.xml, so we need to flush everything
    # first then recreate from scratch
    main_website.menu_id.unlink()
    default_menu = env.ref('website.main_menu')
    main_website.copy_menu_hierarchy(default_menu)