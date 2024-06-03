def migrate(cr, version):
    cr.execute(
        "UPDATE account_report SET prefix_groups_threshold = 4000 WHERE NULLIF(prefix_groups_threshold, 0) IS NULL"
    )
