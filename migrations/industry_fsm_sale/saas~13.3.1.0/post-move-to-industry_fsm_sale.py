# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    env = util.env(cr)
    if util.ref(cr, "industry_fsm.field_service_product"):
        env.ref("industry_fsm_sale.field_service_product", raise_if_not_found=False).unlink()
        util.rename_xmlid(cr, *eb("industry_fsm{{,_sale}}.field_service_product"))
