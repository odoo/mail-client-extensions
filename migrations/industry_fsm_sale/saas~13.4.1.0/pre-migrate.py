# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_project", "allow_quotations", "boolean")
    group_extra_quotation = util.env(cr).ref("industry_fsm_sale.group_fsm_quotation_from_task")
    cr.execute(
        """
        UPDATE project_project
           SET allow_quotations = g.uid IS NOT NULL
          FROM res_groups_users_rel g
         WHERE g.gid = %s;
        """,
        (group_extra_quotation.id,),
    )
