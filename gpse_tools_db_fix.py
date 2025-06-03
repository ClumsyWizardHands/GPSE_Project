"""
Fix for db_manager in tools
"""

# Global variable to hold db_manager instance
_db_manager = None

def set_db_manager(db_manager):
    """Set the global db_manager instance"""
    global _db_manager
    _db_manager = db_manager

def get_db_manager():
    """Get the global db_manager instance"""
    return _db_manager
