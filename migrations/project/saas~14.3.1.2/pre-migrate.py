# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "project.mail_channel_project_task", util.remove_record)
