# -*- coding: utf-8 -*-
from operator import itemgetter

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
            SELECT o.id
              FROM pos_order o
        INNER JOIN pos_session s ON s.id = o.session_id
        INNER JOIN pos_config c ON c.id = s.config_id
        INNER JOIN res_company cmpy ON cmpy.id=o.company_id
        INNER JOIN product_pricelist pp ON pp.id=o.pricelist_id
             WHERE NOT pp.currency_id = cmpy.currency_id
        """
    )
    ids = list(map(itemgetter(0), cr.fetchall()))
    util.recompute_fields(cr, "pos.order", fields=["currency_rate"], ids=ids)
