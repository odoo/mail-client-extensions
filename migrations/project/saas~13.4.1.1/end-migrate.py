# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.remove_field(cr, "project.project", "portal_show_rating")
