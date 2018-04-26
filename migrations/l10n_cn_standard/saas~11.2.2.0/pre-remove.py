# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'l10n_cn_standard.tag1')
    util.remove_record(cr, 'l10n_cn_standard.tag2')
    util.remove_record(cr, 'l10n_cn_standard.vats_standard_business')
    util.remove_record(cr, 'l10n_cn_standard.vatp_standard_business')
