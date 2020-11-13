# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    no_dry_run = lambda model: util.env(cr)[model].with_context(_mig_dry_run=False)
    util.recompute_fields(cr, no_dry_run("slide.slide"), ["total_slides"])
    util.recompute_fields(cr, no_dry_run("slide.channel"), ["total_slides"])
