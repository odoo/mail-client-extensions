# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("CREATE INDEX ON event_mail(template_ref)")
