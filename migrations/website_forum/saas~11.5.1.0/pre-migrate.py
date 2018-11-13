# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record_if_unchanged(cr, "website_forum.validation_email")
