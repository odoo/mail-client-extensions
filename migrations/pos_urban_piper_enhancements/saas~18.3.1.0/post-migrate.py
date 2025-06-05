def migrate(cr, version):
    cr.execute("""
        UPDATE pos_config
           SET urbanpiper_minimum_preparation_time = CEIL(urbanpiper_minimum_preparation_time / 60.0)
    """)
