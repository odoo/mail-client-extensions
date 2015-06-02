from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    Here we have some bootstrapped fields that prevent main process to use
    too much memory and slow down the migration.
    """

    # simple related field to stock quants
    util.create_column(cr, 'stock_quant', 'removal_date',
                       'timestamp without time zone')
    cr.execute("""\
        UPDATE  stock_quant
        SET     removal_date = stock_production_lot.removal_date
        FROM    stock_production_lot
        WHERE   stock_production_lot.id = stock_quant.lot_id;
        """)
