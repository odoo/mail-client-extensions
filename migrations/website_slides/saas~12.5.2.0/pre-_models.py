# -*- coding: utf-8 -*-
from odoo import models
from odoo.addons.website_slides.models import slide_slide as _ignore  # noqa
from odoo.addons.website_slides.models import slide_channel as _ignore  # noqa


def migrate(cr, version):
    pass


class Slide(models.Model):
    _inherit = "slide.slide"
    _module = "website_slides"

    def _compute_slides_statistics(self):
        if self.env.context.get("_mig_dry_run", True):
            return
        return super()._compute_slides_statistics()


class Channel(models.Model):
    _inherit = "slide.channel"
    _module = "website_slides"

    def _compute_slides_statistics(self):
        if self.env.context.get("_mig_dry_run", True):
            return
        return super()._compute_slides_statistics()
