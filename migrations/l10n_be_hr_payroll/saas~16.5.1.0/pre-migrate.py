# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_contract", "has_bicycle", "boolean")
    util.explode_execute(
        cr,
        """
        UPDATE hr_contract c
           SET has_bicycle = true
          FROM hr_employee e
         WHERE e.contract_id = c.id
           AND e.has_bicycle
           AND c.active = true
        """,
        table="hr_contract",
        alias="c",
    )
    util.remove_field(cr, "hr.employee", "has_bicycle")
