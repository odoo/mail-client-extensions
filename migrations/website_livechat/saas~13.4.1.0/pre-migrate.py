# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "website_livechat.menu_livechat", noupdate=True)
