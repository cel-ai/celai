CACHE_DIRECTORY = ".cache"

CACHE_DEFAULT_SETTINGS = {
    'statistics': 0,  # False
    'tag_index': 0,  # False
    'eviction_policy': 'least-recently-stored',
    'size_limit': 2**30,  # 1gb
    'cull_limit': 10,
    'sqlite_auto_vacuum': 1,  # FULL
    'sqlite_cache_size': 2**13,  # 8,192 pages
    'sqlite_journal_mode': 'wal',
    'sqlite_mmap_size': 2**26,  # 64mb
    'sqlite_synchronous': 1,  # NORMAL
    'disk_min_file_size': 2**15,  # 32kb
}