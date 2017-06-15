# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.delete_model(cr, 'report.stock.lines.date')
    util.remove_view(cr, 'stock.report_stock_lines_date_tree')
    util.remove_view(cr, 'stock.report_stock_lines_date_search')
    util.remove_view(cr, 'stock.report_stock_lines_date_form')
    util.remove_record(cr, 'stock.action_stock_line_date')
    util.remove_record(cr, 'stock.menu_report_stock_line_date')
