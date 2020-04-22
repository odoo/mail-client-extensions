# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("data_merge_crm.data_merge_model_crm{_lead,}_tag"))
    util.rename_xmlid(cr, *eb("data_merge_crm.data_merge_field_crm{_lead,}_tag_name"))
