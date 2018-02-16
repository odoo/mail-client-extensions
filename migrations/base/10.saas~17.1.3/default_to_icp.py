# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def default_to_icp(cr, model, field, key):
    # convert a default value into a ICP value
    # used in saas~17 scripts to adapt setting wizards
    e = util.env(cr)
    if util.table_exists(cr, 'ir_values'):
        dv = e['ir.values'].get_default(model, field)
        cr.execute("DELETE FROM ir_values WHERE key='default' AND model=%s AND name=%s",
                   [model, field])
    else:
        # we are already in saas~18, use new `ir.default` model
        dv = e['ir.default'].get(model, field)
        fid = e['ir.model.fields']._get(model, field).id
        if fid:
            cr.execute('DELETE FROM ir_default WHERE field_id=%s', [fid])

    if dv:
        e['ir.config_parameter'].set_param(key, '%s' % (dv,))
