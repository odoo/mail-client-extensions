# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
            INSERT INTO hr_departure_reason(name, create_uid, create_date, write_uid, write_date)
                 SELECT initcap(trim(departure_reason)), 1, now() at time zone 'utc', 1, now() at time zone 'utc'
                   FROM hr_employee e
                  WHERE e.departure_reason IS NOT NULL
                    AND NOT EXISTS (SELECT 1 FROM hr_departure_reason hdr WHERE lower(hdr.name) = lower(e.departure_reason))
               GROUP BY initcap(trim(e.departure_reason))
        """
    )

    cr.execute(
        """
            UPDATE hr_employee emp
               SET departure_reason_id = dep.id
              FROM hr_departure_reason dep
             WHERE lower(emp.departure_reason) = lower(dep.name)
        """
    )

    util.update_field_references(cr, "departure_reason", "departure_reason_id", only_models=("hr.employee",))
    util.remove_field(cr, "hr.employee", "departure_reason")
