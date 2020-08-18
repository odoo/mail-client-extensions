# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, 'social_push_notifications.social_push_notifications_layout')
