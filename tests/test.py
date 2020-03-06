import support_functions
import vm_functions
import unittest


class TestStringMethods(unittest.TestCase):
    # vm_functions options
    vm_functions.logging.disable()
    vm_functions.vboxmanage_path = 'vboxmanage'
    vm_functions.timeout = 60

    def test_file_info(self):
        result = support_functions.file_info('../putty.exe')
        self.assertEqual(result, 0)

    def test_file_info_nonexisted(self):
        result = support_functions.file_info('nonexisted')
        self.assertEqual(result, 1)

    def test_virtualbox_version(self):
        result = vm_functions.virtualbox_version()
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], '6.1.4r136177\n')
        self.assertEqual(result[2], '')

    def test_vm_start_good(self):
        result = vm_functions.vm_start('w10_x64')
        self.assertEqual(result[0], 0)
        self.assertRegex(result[1], 'VM "w10_x64" has been successfully started.')
        self.assertEqual(result[2], '')

    def test_vm_start_nonexisting(self):
        result = vm_functions.vm_start('nonexisted')
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'Could not find a registered machine')

    # def test_vm_upload(self):
    #     result = vm_functions.vm_upload('w10_x64', 'addm', 'P@ssw0rd', '../putty.exe', 'C:\\putty.exe')
    #     self.assertEqual(result[0], 0)
    #     self.assertEqual(result[1], '')
    #     self.assertEqual(result[2], '')
    #
    # def test_vm_upload_nonexisting_file(self):
    #     result = vm_functions.vm_upload('w10_x64', 'username', 'P@ssw0rd', 'nonexisting.file', 'C:\\putty.exe')
    #     self.assertEqual(result[0], 1)
    #     self.assertEqual(result[1], '')
    #     self.assertEqual(result[2], '')
    #
    # def test_vm_upload_incorrect_credentials(self):
    #     result = vm_functions.vm_upload('w10_x64', 'nonexisting_user', 'P@ssw0rd', '../putty.exe', 'C:\\putty.exe')
    #     self.assertEqual(result[0], 1)
    #     self.assertEqual(result[1], '')
    #     self.assertEqual(result[2], '')
    #
    # def test_vm_download(self):
    #     result = vm_functions.vm_download('w10_x64', 'addm', 'P@ssw0rd', '../putty.exe', 'C:\\putty.exe')
    #     self.assertEqual(result[0], 0)
    #     self.assertEqual(result[1], '')
    #     self.assertEqual(result[2], '')
    #
    # def test_vm_download_incorrect_credentials(self):
    #     result = vm_functions.vm_download('w10_x64', 'nonexisting_user', 'P@ssw0rd', '../putty.exe', 'C:\\putty.exe')
    #     self.assertEqual(result[0], 1)
    #     self.assertEqual(result[1], '')
    #     self.assertEqual(result[2], '')
    #
    # def test_vm_download_nonexisting_file(self):
    #     result = vm_functions.vm_download('w10_x64', 'user', 'P@ssw0rd', 'nonexisting.file', '../putty.exe')
    #     self.assertEqual(result[0], 1)
    #     self.assertEqual(result[1], '')
    #     self.assertEqual(result[2], '')

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

    def test_vm_snapshot_restore_good(self):
        result = vm_functions.vm_snapshot_restore('w10_x64', 'live')
        self.assertEqual(result[0], 0)
        self.assertRegex(result[1], 'Restoring snapshot')
        self.assertRegex(result[2], '100%')

    def test_vm_snapshot_restore_nonexisting1(self):
        result = vm_functions.vm_snapshot_restore('w10_x64', 'nonexisted')
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'Could not find a snapshot')

    def test_vm_snapshot_restore_nonexisting2(self):
        result = vm_functions.vm_snapshot_restore('nonexisted', 'nonexisted')
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'Could not find a registered machine')

    def test_list_ips(self):
        result = vm_functions.list_ips('w10_x64')
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], ['172.22.90.227'])
        self.assertEqual(result[2], '')


if __name__ == '__main__':
    unittest.main()

