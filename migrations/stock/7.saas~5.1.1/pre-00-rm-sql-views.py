from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        -- the following views are deprecated since 7.saas~5
        DROP VIEW IF EXISTS stock_report_tracklots;
        DROP VIEW IF EXISTS stock_report_prodlots;
        DROP VIEW IF EXISTS report_stock_inventory;
        DROP VIEW IF EXISTS report_stock_move;
        """
    )

    util.remove_model(cr, "report.stock.move")
