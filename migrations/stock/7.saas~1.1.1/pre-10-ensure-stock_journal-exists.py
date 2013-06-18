from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.ensure_xmlid_match_record(cr, 'stock.stock_journal', 'account.journal', {
        'code': 'STJ',
        'company_id': util.ref(cr, 'base.main_company'),
    })
