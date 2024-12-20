def migrate(cr, version):
    cr.execute("DROP SEQUENCE IF EXISTS base_registry_signaling")
    cr.execute("DROP SEQUENCE IF EXISTS base_cache_signaling")  # maybe an old one pre multiple orm cache
    cr.execute("DROP SEQUENCE IF EXISTS base_cache_signaling_default")
    cr.execute("DROP SEQUENCE IF EXISTS base_cache_signaling_assets")
    cr.execute("DROP SEQUENCE IF EXISTS base_cache_signaling_templates")
    cr.execute("DROP SEQUENCE IF EXISTS base_cache_signaling_routing")
    cr.execute("DROP SEQUENCE IF EXISTS base_cache_signaling_groups")
