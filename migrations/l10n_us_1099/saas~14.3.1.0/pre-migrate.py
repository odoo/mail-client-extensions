# -*- coding: utf-8 -*-
import logging

from odoo.upgrade import util


def migrate(cr, version):
    logger = logging.getLogger("odoo.modules.loading")
    util.ENVIRON["l10n_us_1099_loglevel"] = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)
