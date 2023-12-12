# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

# NOTE: this code is located in base because it should be triggered before crm
#       and sales_team (but sales_team is a new module so it doesn't run the
#       migration scripts)


def migrate(cr, version):
    # NOTE: these data are conflicting because they are both using the
    #       code "DM" but crm.crm_case_section_3 exists only if the demo data
    #       are installed.
    if util.ref(cr, "crm.crm_case_section_3"):
        # remove duplicate record related sales_team
        cr.execute(
            """DELETE FROM ir_model_data
                                WHERE  model = 'crm.case.section'
                                  AND name = 'section_sales_department'
                   """
        )

        # rename xmlid of record related to sales_team
        util.rename_xmlid(cr, "crm.crm_case_section_3", "crm.section_sales_department")
