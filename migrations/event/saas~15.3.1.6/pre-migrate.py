# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("CREATE INDEX tmp_mig_eventmailtemplate_speedup_idx ON event_mail(template_ref)")
    util.ENVIRON["__created_fk_idx"].append("tmp_mig_eventmailtemplate_speedup_idx")
