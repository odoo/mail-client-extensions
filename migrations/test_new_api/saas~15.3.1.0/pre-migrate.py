# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    if util.table_exists(cr, "test_new_api_prefetch_translate"):  # model added in saas~15.2
        util.rename_model(cr, *eb("test_new_api.prefetch{.translate,}"))
        util.rename_xmlid(cr, *eb("test_new_api.access_test_new_api_prefetch{_translate,}"))
