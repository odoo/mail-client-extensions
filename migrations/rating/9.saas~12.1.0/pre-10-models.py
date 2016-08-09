# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'rating_rating', 'consumed', 'boolean')
    cr.execute("UPDATE rating_rating SET consumed = (rating != -1)")
    cr.execute("UPDATE rating_rating SET rating=0 WHERE rating = -1")
