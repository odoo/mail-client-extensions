# -*- coding: utf-8 -*-
import base64
import json
try:
    from odoo.tools import pickle as cPickle
except ImportError:
    try:
        import cPickle
    except ImportError:
        import pickle as cPickle

from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for cache in util.env(cr)['pos.cache'].search([]):
        data = cPickle.loads(base64.decodestring(cache.cache))
        cache.write({
            'cache': base64.encodestring(json.dumps(data).encode('utf-8'))
        })
