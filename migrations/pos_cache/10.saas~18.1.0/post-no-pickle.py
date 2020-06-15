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
    PosCache = util.env(cr)["pos.cache"]
    ids = PosCache.search([]).ids
    for cache in util.iter_browse(PosCache, ids, chunk_size=1):
        if not cache.cache:
            # We don't have the data because the filestore is not available.
            # force a refresh at next loading.
            cache.write({"cache": False})
        else:
            data = cPickle.loads(base64.decodebytes(cache.cache))
            cache.write({"cache": base64.encodebytes(json.dumps(data).encode("utf-8"))})
