#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forkast_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # cx_Oracle Shim for oracledb
    try:
        import oracledb
        import sys
        oracledb.version = "8.3.0"
        
        # Django's Oracle backend expects these to be types for isinstance()
        if not isinstance(getattr(oracledb, 'Binary', None), type):
            class Binary(bytes): pass
            oracledb.Binary = Binary
        
        if not isinstance(getattr(oracledb, 'Timestamp', None), type):
            import datetime
            oracledb.Timestamp = datetime.datetime

        # Map some common cx_Oracle attributes if missing
        attr_map = {
            'DATETIME': 'DB_TYPE_DATE',
            'STRING': 'DB_TYPE_VARCHAR',
            'NUMBER': 'DB_TYPE_NUMBER',
            'CURSOR': 'DB_TYPE_CURSOR',
            'FIXED_CHAR': 'DB_TYPE_CHAR',
            'FIXED_UNICODE': 'DB_TYPE_NCHAR',
            'UNICODE': 'DB_TYPE_NVARCHAR',
            'LONG_STRING': 'DB_TYPE_LONG',
            'LONG_UNICODE': 'DB_TYPE_LONG_NVARCHAR',
            'NCLOB': 'DB_TYPE_NCLOB',
            'CLOB': 'DB_TYPE_CLOB',
            'BLOB': 'DB_TYPE_BLOB',
            'BFILE': 'DB_TYPE_BFILE',
            'ROWID': 'DB_TYPE_ROWID',
        }
        for old, new in attr_map.items():
            if not hasattr(oracledb, old) and hasattr(oracledb, new):
                setattr(oracledb, old, getattr(oracledb, new))

        sys.modules["cx_Oracle"] = oracledb
    except ImportError:
        pass

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
