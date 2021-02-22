# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    task_rating_id = util.ref(cr, 'project.mt_task_rating')
    cr.execute("UPDATE mail_message_subtype SET description = NULL WHERE id = %s", [task_rating_id])
    util.remove_field(cr, "project.task", "ribbon_message")
