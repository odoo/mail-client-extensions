# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE resource_resource r
           SET default_role_id = e.default_planning_role_id
          FROM hr_employee e
         WHERE e.resource_id = r.id
        """
    )
    cr.execute(
        """
        INSERT INTO resource_resource_planning_role_rel
                    (resource_resource_id, planning_role_id)
             SELECT r.id,
                    r.default_role_id
               FROM resource_resource r
              WHERE r.default_role_id IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )
    util.remove_column(cr, "hr_employee", "default_planning_role_id")
