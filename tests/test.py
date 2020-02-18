import support_functions
import vm_functions
import unittest


class TestStringMethods(unittest.TestCase):
    # Disable logging
    vm_functions.logging.disable()

    def test_file_info(self):
        result = support_functions.file_info('../putty.exe')
        self.assertEqual(result, 0)

    def test_file_info_nonexisted(self):
        result = support_functions.file_info('nonexisted')
        self.assertEqual(result, 1)

    def test_virtualbox_version(self):
        result = vm_functions.vm_version()
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], '6.1.2r135662\n')
        self.assertEqual(result[2], '')

    def test_vm_start_good(self):
        result = vm_functions.vm_start('w10_x64')
        self.assertEqual(result[0], 0)
        self.assertRegex(result[1], 'VM "w10_x64" has been successfully started.')
        self.assertEqual(result[2], '')

    def test_vm_start_nonexisted(self):
        result = vm_functions.vm_start('nonexisted')
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'Could not find a registered machine')

    def test_vm_stop_running(self):
        result = vm_functions.vm_stop('w10_x64')
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], '100%')

    def test_vm_stop_stopped(self):
        result = vm_functions.vm_stop('w10_x64')
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'Invalid machine state: PoweredOff')

    def test_vm_restore_snapshot_good(self):
        result = vm_functions.vm_restore('w10_x64', '2020-01')
        self.assertEqual(result[0], 0)
        self.assertRegex(result[1], 'Restoring snapshot')
        self.assertRegex(result[2], '100%')

    def test_vm_restore_snapshot_nonexisted1(self):
        result = vm_functions.vm_restore('w10_x64', 'nonexisted')
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'Could not find a snapshot')

    def test_vm_restore_snapshot_nonexisted2(self):
        result = vm_functions.vm_restore('nonexisted', 'nonexisted')
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'Could not find a registered machine')


if __name__ == '__main__':
    unittest.main()

