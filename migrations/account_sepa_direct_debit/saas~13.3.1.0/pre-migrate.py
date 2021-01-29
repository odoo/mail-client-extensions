# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)

    ''' sdd_mandate original_doc must be converted to ir.attachment '''
    cr.execute('''
    SELECT
        COALESCE(original_doc_filename, 'mandate_file') as name,
        original_doc as datas,
        'sdd.mandate' as res_model,
        id as res_id,
        create_uid,
        create_date,
        write_uid,
        write_date
    FROM
        sdd_mandate
    WHERE
        original_doc IS NOT NULL
    ''')
    env['ir.attachment'].create(cr.dictfetchall())
    util.remove_field(cr, 'sdd.mandate', 'original_doc')
    util.remove_field(cr, 'sdd.mandate', 'original_doc_filename')

    ''' create sdd_scheme columns & set default value '''
    util.create_column(cr, 'sdd_mandate', 'sdd_scheme', 'varchar')
    cr.execute("UPDATE sdd_mandate SET sdd_scheme = 'CORE'")
    util.create_column(cr, 'account_batch_payment', 'sdd_scheme', 'varchar')
    cr.execute("UPDATE account_batch_payment SET sdd_scheme = 'CORE'")
