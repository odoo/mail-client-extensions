# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_xmlid(cr, *eb("industry_fsm{_sale,}.group_fsm_quotation_from_task"))
    util.move_field_to_module(cr, "res.config.settings", "group_industry_fsm_quotations", *eb("industry_fsm{_sale,}"))
