# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("website_slides_survey.survey_{templates,closed_finished}_inherit_website_slides"))
