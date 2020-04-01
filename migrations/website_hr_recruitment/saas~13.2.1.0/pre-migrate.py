# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    for by in "countries departments offices".split():
        util.rename_xmlid(cr, *eb(f"website_hr_recruitment.job_{{,filter_by_}}{by}"))
