# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
from odoo.modules.db import create_categories

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("base.module_category_{hr_appraisal,human_resources_appraisals}"))
    util.rename_xmlid(cr, *eb("base.module_category_{,communication_}sign"))
    util.rename_xmlid(cr, *eb("base.module_category_{,operations_}helpdesk"))

    #Category renaming
    for category in (
        'Operations/Timesheets',
        'Accounting/Invoicing',
        "Marketing/Marketing Automation",
        'Marketing/Email Marketing',
        'Manufacturing/PLM',
        'Manufacturing/Quality',
        'Manufacturing/Manufacturing',
        'Sales/Sales',
        'Operations/Project',
        'Operations/Inventory',
        'Website/Website'
    ):
        create_categories(cr, category.split('/'))
