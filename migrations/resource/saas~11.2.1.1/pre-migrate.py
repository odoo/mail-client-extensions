# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for table, column, _, delete_action in util.get_fk(cr, 'resource_resource'):
        if column != 'resource_id' or delete_action != 'r':
            # does not look like from mixin
            continue

        util.create_column(cr, table, 'resource_calendar_id', 'int4')
        cr.execute("""
            UPDATE {} t
               SET resource_calendar_id = r.calendar_id
              FROM resource_resource r
             WHERE t.resource_id = r.id
        """.format(table))
