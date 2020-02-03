# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.import_script("base/saas~12.5.1.3/pre-21-images.py").single_image(cr, "mail.channel")
