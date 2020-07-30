# -*- coding: utf-8 -*-
import psycopg2

from odoo.tools import ignore
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.move_field_to_module(cr, "sale.order.line", "product_template_id", "sale_product_configurator", "sale")

    util.create_column(cr, "account_move", "team_id", "int4")
    util.create_column(cr, "account_move", "partner_shipping_id", "int4")

    with ignore(psycopg2.Error), util.savepoint(cr):
        # fields can already be there (moved from `website_sale_link_tracker` module)
        for field in {"campaign_id", "medium_id", "source_id"}:
            util.move_field_to_module(cr, "sale.order", field, "sale_crm", "sale")
