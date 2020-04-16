# -*- coding: utf-8 -*-
import itertools
from odoo.upgrade import util


def migrate(cr, version):
    module = "l10n_cn" if util.version_gte("saas~13.2") else "l10n_cn_small_business"
    dimensions = [
        {"sales", "purchase"},
        {"included", "excluded"},
        {"17", "11", "3"},
    ]

    for x, y, z in itertools.product(*dimensions):
        util.remove_record(cr, f"{module}.l10n_cn_small_business_{x}_{y}_{z}")
