# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE repair_order o
           SET company_id = l.company_id
          FROM stock_location l
         WHERE l.id = o.location_id
           AND o.company_id IS NULL
    """
    )

    util.create_column(cr, "repair_line", "company_id", "int4")
    cr.execute(
        """
        UPDATE repair_line l
           SET company_id = o.company_id
          FROM repair_order o
         WHERE o.id = l.repair_id
           AND l.company_id IS NULL
    """
    )

    util.create_column(cr, "repair_fee", "company_id", "int4")
    cr.execute(
        """
        UPDATE repair_fee f
           SET company_id = o.company_id
          FROM repair_order o
         WHERE o.id = f.repair_id
           AND f.company_id IS NULL
    """
    )

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("repair.repair_{,order_}rule"))
