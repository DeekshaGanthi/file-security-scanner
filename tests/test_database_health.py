from unittest.mock import MagicMock, patch
from backend.database import check_database, get_connection


def test_readiness_executes_select_without_writes():
    pool = MagicMock()
    pool.kwargs = {'host': 'private-db', 'connect_timeout': 2}
    with patch('backend.database.get_pool', return_value=pool), patch('backend.database.psycopg.connect') as connect:
        check_database()
        connect.assert_called_once_with(host='private-db', connect_timeout=2)
        cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.execute.assert_called_once_with('SELECT 1')
        cursor.fetchone.assert_called_once()


def test_database_connections_return_to_pool():
    pool = MagicMock()
    with patch('backend.database.get_pool', return_value=pool):
        with get_connection() as connection:
            assert connection is pool.connection.return_value.__enter__.return_value
    pool.connection.assert_called_once_with(timeout=2)
    pool.connection.return_value.__exit__.assert_called_once()
