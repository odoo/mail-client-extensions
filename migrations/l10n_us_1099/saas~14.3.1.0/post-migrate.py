# -*- coding: utf-8 -*-
import logging

from odoo.upgrade import util


def migrate(cr, version):
    logger = logging.getLogger("odoo.modules.loading")
    logger.setLevel(util.ENVIRON["l10n_us_1099_loglevel"])
