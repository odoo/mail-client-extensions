# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    views = """
        rating_index
        portal_project_rating_progressbar
        portal_project_rating_partner_stat
        portal_project_rating_popover
        rating_project_rating_page
    """

    if util.module_installed(cr, "website_project"):
        for view in util.splitlines(views):
            util.rename_xmlid(cr, f"project.{view}", f"website_project.{view}")
    else:
        for view in util.splitlines(views):
            util.remove_view(cr, f"project.{view}")
