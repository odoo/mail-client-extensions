# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Rename publisher into restricted editor
    util.rename_xmlid(
        cr,
        "website_profile.gamification_karma_rank_access_website_publisher",
        "website_profile.gamification_karma_rank_access_restricted_editor",
    )
