def migrate(cr, version):
    cr.execute("DROP VIEW IF EXISTS report_industry_fsm_report_worksheet_custom CASCADE")
