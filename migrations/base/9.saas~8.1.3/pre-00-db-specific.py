# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _lumossolar(cr, version):
    # I don't know the origin of theses states (csv import?)
    # but they don't below to 'base' module.
    cr.execute("""
        UPDATE ir_model_data
           SET module='__export__'
         WHERE model='res.country.state'
           AND module='base'
           AND id > 10000
    """)

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '51f95bab-bcd3-4361-b863-75abe5b399a7': _lumossolar,
    })
