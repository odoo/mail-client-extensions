# -*- coding: utf-8 -*-

from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    env = util.env(cr)

    # Force recomputation of department complete_name in topological order
    Department = env['hr.department']
    cr.execute("""
        WITH RECURSIVE department(id, parent_id) AS (
            SELECT id, NULL::integer FROM hr_department WHERE parent_id IS NULL
            UNION ALL
            (
                SELECT d.id, d.parent_id
                FROM hr_department d, department AS parent_dep
                WHERE d.parent_id = parent_dep.id
            )
        )
        SELECT id FROM department;
    """)
    dep_topo_ids = [id_ for id_, in cr.fetchall()]
    util.recompute_fields(cr, Department, ['complete_name'], dep_topo_ids)
