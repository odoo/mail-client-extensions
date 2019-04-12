# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # a required=True without cascade deletion  on the uninstall wizard can prevent
    # module deletion (module_id on the wizard is a not null fkey)
    # apply the cascade deletion pre-emptively to avoid stupid restrictions
    cr.execute('''ALTER TABLE base_module_uninstall
                  DROP CONSTRAINT base_module_uninstall_module_id_fkey,
                  ADD CONSTRAINT base_module_uninstall_module_id_fkey
                    FOREIGN KEY (module_id)
                    REFERENCES ir_module_module(id)
                    ON DELETE CASCADE
               ''')
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
        util.new_module(cr, "quality_control", deps=("quality",))
        if util.module_installed(cr, "quality"):
            # module `quality` has been splitted. Keep behavior
            util.force_install_module(cr, "quality_control")

        util.module_deps_diff(cr, 'mrp_maintenance', plus={'mrp_workorder'}, minus={'quality_mrp'})
        util.module_deps_diff(cr, 'mrp_workorder', plus={'quality'})
        util.module_deps_diff(cr, 'quality_mrp', plus={'quality_control', 'mrp'}, minus={'mrp_workorder', 'quality'})
        util.new_module(cr, 'quality_mrp_workorder', deps=('quality_control', 'mrp_workorder'), auto_install=True)

        util.new_module(cr, 'test_marketing_automation', deps=('marketing_automation', 'test_mail'))

    util.remove_module(cr, 'sale_service_rating')
