# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # description of 'project.task' is now an html field

    cr.execute("""UPDATE project_task
                     SET description={}
                   WHERE description IS NOT NULL
               """.format(util.pg_text2html('description')))
