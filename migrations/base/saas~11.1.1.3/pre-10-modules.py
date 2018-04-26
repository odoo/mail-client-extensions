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

    if util.has_enterprise():
        util.module_deps_diff(cr, 'mrp_maintenance', plus={'mrp_workorder'}, minus={'quality_mrp'})
        util.module_deps_diff(cr, 'mrp_workorder', plus={'quality'})
        util.new_module(cr, 'quality_control', deps=('quality',), auto_install=True)
        util.module_deps_diff(cr, 'quality_mrp', plus={'quality_control', 'mrp'}, minus={'mrp_workorder', 'quality'})
        util.new_module(cr, 'quality_mrp_workorder', deps=('quality_control', 'mrp_workorder'), auto_install=True)

        util.new_module(cr, 'test_marketing_automation', deps=('marketing_automation', 'test_mail'))

    util.remove_module(cr, 'sale_service_rating')
