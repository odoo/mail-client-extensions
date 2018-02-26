# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.new_module_dep(cr, 'l10n_mx', 'account_cancel')

    util.merge_module(cr, 'rating_project', 'project')
    util.merge_module(cr, 'website_rating_project', 'project')
    util.module_deps_diff(cr, 'project', plus={'rating'}, minus={'website'})

    util.new_module(cr, 'test_mail', deps={'test_performance', 'mail'})
    util.remove_module_deps(cr, 'test_performance', ('mail',))
    util.new_module(cr, 'test_testing_utilities', deps={'base'})

    util.new_module_dep(cr, 'web_settings_dashboard', 'web')

    util.new_module(cr, 'website_sale_link_tracker', deps={'website_sale', 'website_links'}, auto_install=True)

    util.remove_module(cr, 'sale_service_rating')
    util.remove_module(cr, 'web_planner')
