# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("UPDATE mail_template SET user_signature=true WHERE id=%s",
               [util.ref(cr, "project.mail_template_data_project_task")])

    cr.execute("UPDATE mail_template SET user_signature=false WHERE id=%s",
               [util.ref(cr, "project.rating_project_request_email_template")])
