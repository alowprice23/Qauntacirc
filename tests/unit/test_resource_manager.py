import unittest
from unittest.mock import patch, MagicMock

from core.resource_manager import ResourceManager

class TestResourceManager(unittest.TestCase):

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_no_limits(self, mock_virtual_memory, mock_cpu_percent):
        """Test that is_within_limits returns True when no limits are set."""
        resource_manager = ResourceManager()
        self.assertTrue(resource_manager.is_within_limits())
        mock_cpu_percent.assert_not_called()
        mock_virtual_memory.assert_not_called()

    @patch('psutil.cpu_percent', return_value=50.0)
    @patch('psutil.virtual_memory')
    def test_cpu_limit_within_bounds(self, mock_virtual_memory, mock_cpu_percent):
        """Test CPU check when usage is below the limit."""
        resource_manager = ResourceManager(cpu_limit=80.0)
        self.assertTrue(resource_manager.is_within_limits())
        mock_cpu_percent.assert_called_once()
        mock_virtual_memory.assert_not_called()

    @patch('psutil.cpu_percent', return_value=90.0)
    @patch('psutil.virtual_memory')
    def test_cpu_limit_exceeded(self, mock_virtual_memory, mock_cpu_percent):
        """Test CPU check when usage is above the limit."""
        resource_manager = ResourceManager(cpu_limit=80.0)
        self.assertFalse(resource_manager.is_within_limits())
        mock_cpu_percent.assert_called_once()

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_memory_limit_within_bounds(self, mock_virtual_memory, mock_cpu_percent):
        """Test memory check when usage is below the limit."""
        mock_virtual_memory.return_value = MagicMock(percent=60.0)
        resource_manager = ResourceManager(memory_limit=80.0)
        self.assertTrue(resource_manager.is_within_limits())
        mock_virtual_memory.assert_called_once()
        mock_cpu_percent.assert_not_called()

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_memory_limit_exceeded(self, mock_virtual_memory, mock_cpu_percent):
        """Test memory check when usage is above the limit."""
        mock_virtual_memory.return_value = MagicMock(percent=95.0)
        resource_manager = ResourceManager(memory_limit=80.0)
        self.assertFalse(resource_manager.is_within_limits())
        mock_virtual_memory.assert_called_once()

    @patch('psutil.cpu_percent', return_value=90.0)
    @patch('psutil.virtual_memory')
    def test_both_limits_cpu_exceeded(self, mock_virtual_memory, mock_cpu_percent):
        """Test with both limits set, CPU exceeds."""
        mock_virtual_memory.return_value = MagicMock(percent=50.0)
        resource_manager = ResourceManager(cpu_limit=80.0, memory_limit=80.0)
        self.assertFalse(resource_manager.is_within_limits())

    @patch('psutil.cpu_percent', return_value=70.0)
    @patch('psutil.virtual_memory')
    def test_both_limits_memory_exceeded(self, mock_virtual_memory, mock_cpu_percent):
        """Test with both limits set, memory exceeds."""
        mock_virtual_memory.return_value = MagicMock(percent=90.0)
        resource_manager = ResourceManager(cpu_limit=80.0, memory_limit=80.0)
        self.assertFalse(resource_manager.is_within_limits())

    @patch('psutil.cpu_percent', return_value=70.0)
    @patch('psutil.virtual_memory')
    def test_get_current_usage(self, mock_virtual_memory, mock_cpu_percent):
        """Test the get_current_usage method."""
        mock_virtual_memory.return_value = MagicMock(percent=55.5)
        resource_manager = ResourceManager()
        usage = resource_manager.get_current_usage()
        self.assertEqual(usage['cpu_percent'], 70.0)
        self.assertEqual(usage['memory_percent'], 55.5)


if __name__ == '__main__':
    unittest.main()