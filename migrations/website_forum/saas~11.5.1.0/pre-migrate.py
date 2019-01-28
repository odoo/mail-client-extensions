# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_forum.validation_email", util.update_record_from_xml)
    util.remove_view(cr, "website_forum.content_new_forum")
