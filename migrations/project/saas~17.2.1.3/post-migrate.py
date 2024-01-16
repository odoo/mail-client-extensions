# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "project.mail_template_data_project_task", util.update_record_from_xml)
