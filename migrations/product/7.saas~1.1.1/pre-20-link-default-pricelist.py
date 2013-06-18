from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        A default pricelist is created by xml data.
        If user deleted and recreated pricelist, we can't recreate a new one that overlap.
        We need to match xmlids, to the existing pricelists.
        As pricelists are in "noupdate" mode, that's not a problem to reassign xmlids...
    """
    pl_id = util.ensure_xmlid_match_record(cr, 'product.list0', 'product.pricelist', {'type': 'sale'})
    if pl_id:
        plv_id = util.ensure_xmlid_match_record(cr, 'product.ver0', 'product.pricelist.version', {
            'pricelist_id': pl_id,
            'date_start': None,
            'date_end': None,
        })
        if not plv_id:
            util.remove_record(cr, 'product.ver0')
            util.remove_record(cr, 'product.item0')
        else:
            util.ensure_xmlid_match_record(cr, 'product.item0', 'product.pricelist.item', {
                'price_version_id': plv_id,
                'base': util.ref(cr, 'product.list_price'),
            })
