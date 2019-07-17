# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE ir_model_data SET module = '__import__' WHERE module ='' OR module IS NULL")

# SHORT VERSION
# ==============
# In v11, we can get null in ir_model_data.module when you import.
# In v12, this cause issue (export-import creates duplicates)
#
#
# LONG VERSION
# =============
# In v11, if you imported records with a custom external identifier (in this case, specifying it)
# (see documentation: https://www.odoo.com/documentation/user/11.0/general/base_import/import_faq.html),
# if you did not add a name like "something.a_unique_identifier" but just "a_unique_identifier"
# (as it is showed in the documentation example)
# the new external identifier was created with "a_unique_identifier" as name and an empty string as module.
# This would be ok and would not pose any problems.
#
# In v12 Those databases experience a weird behavior:
# When exporting the records, editing and importing them back, instead of updating the existing record, a new one is created.
# This is the result of a change in the way of loading imported records.
# When exporting the records without a module in their external identifier there is not a problem
# (the incomplete (without first part before the dot) external identifier is exported).
# But when importing back, if the system identifies an external identifier without module
# (without anything before the dot) it adds "__import__" so it becomes "__import__.old_external_identifier".
# The system, thus, does not identify it as the existing record (which identifier is just "old_external_identifier") and creates a new record,
# which will be updated every time a csv/excel file is imported from now on.