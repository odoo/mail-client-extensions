# -*- coding: utf-8 -*-
from odoo.addons.l10n_mx_edi_extended import post_init_hook

from odoo.upgrade import util


def migrate(cr, version):
    post_init_hook(cr, util.env(cr))
