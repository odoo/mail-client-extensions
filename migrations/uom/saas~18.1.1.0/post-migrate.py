def migrate(cr, version):
    cr.execute("""
        UPDATE uom_uom
           SET factor = relative_factor
         WHERE relative_factor IS NOT NULL
    """)
