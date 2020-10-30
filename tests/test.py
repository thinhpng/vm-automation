import support_functions
import vm_functions
import unittest

version_good = '6.1.16r140961'
vm_good = 'w10_x64_2004'
vm_bad = 'donotexist'
snapshot_good = 'live'
snapshot_bad = 'donotexist'
file_good = '../file.exe'
file_bad = '../donotexist.exe'
file_dst = 'C:\\windows\\temp\\file.exe'
user_good = 'admin'
user_bad = 'donotexist'
pass_good = '12345678'
pass_bad = 'wrongpass'
ips_good = ['10.1.0.14', '169.254.153.199']


class TestStringMethods(unittest.TestCase):
    # vm_functions options
    vm_functions.logging.disable()
    vm_functions.vboxmanage_path = 'vboxmanage'
    vm_functions.timeout = 60

    def test01_file_info(self):
        result = support_functions.file_info(file_good)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], '736330aaa3a4683d3cc866153510763351a60062a236d22b12f4fe0f10853582')
        self.assertEqual(result[2], '9052d06c6ac53471f8496263f8fef2eb')
        self.assertEqual(result[3], 1070)

    def test02_file_info_nonexisted(self):
        result = support_functions.file_info(file_bad)
        self.assertEqual(result, 1)

    def test03_virtualbox_version(self):
        result = vm_functions.virtualbox_version()
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], version_good)
        self.assertEqual(result[2], '')

    def test04_vm_start_good(self):
        result = vm_functions.vm_start(vm_good)
        self.assertEqual(result[0], 0)
        self.assertRegex(result[1], f'VM "{vm_good}" has been successfully started.')
        self.assertEqual(result[2], '')

    def test05_vm_start_nonexisting(self):
        result = vm_functions.vm_start(vm_bad)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'Could not find a registered machine')

    def test06_vm_upload(self):
        result = vm_functions.vm_upload(vm_good, user_good, pass_good, file_good, file_dst)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], '')
        self.assertEqual(result[2], '')

    def test07_vm_upload_nonexisting_file(self):
        result = vm_functions.vm_upload(vm_good, user_good, pass_good, file_bad, file_dst)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'VERR_FILE_NOT_FOUND')

    def test08_vm_upload_incorrect_credentials(self):
        result = vm_functions.vm_upload(vm_good, user_bad, pass_bad, file_good, file_dst)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'The specified user was not able to logon on guest')

    def test09_vm_download_incorrect_credentials(self):
        result = vm_functions.vm_download(vm_good, user_good, pass_bad, file_bad, file_dst)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'The specified user was not able to logon on guest')

    def test10_vm_download_nonexisting_file(self):
        result = vm_functions.vm_download(vm_good, user_good, pass_good, file_dst, file_bad)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'Querying guest file information failed')

    def test11_vm_stop_running(self):
        result = vm_functions.vm_stop(vm_good)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], '100%')

    def test12_vm_stop_stopped(self):
        result = vm_functions.vm_stop(vm_good)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'is not currently running')

    def test13_vm_snapshot_restore_good(self):
        result = vm_functions.vm_snapshot_restore(vm_good, snapshot_good)
        self.assertEqual(result[0], 0)
        self.assertRegex(result[1], 'Restoring snapshot')
        self.assertRegex(result[2], '100%')

    def test14_vm_snapshot_restore_nonexisting_a(self):
        result = vm_functions.vm_snapshot_restore(vm_good, snapshot_bad)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'Could not find a snapshot')

    def test15_vm_snapshot_restore_nonexisting_b(self):
        result = vm_functions.vm_snapshot_restore(vm_bad, snapshot_bad)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], '')
        self.assertRegex(result[2], 'Could not find a registered machine')

    def test16_list_ips(self):
        result = vm_functions.list_ips(vm_good)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], ips_good)
        self.assertEqual(result[2], '')

    # def test17_vm_start_good_config(self):
    #     result = vm_functions.vm_start(vm_good)
    #     self.assertEqual(result[0], 0)
    #     self.assertRegex(result[1], f'VM "{vm_good}" has been successfully started.')
    #     self.assertEqual(result[2], '')


if __name__ == '__main__':
    unittest.main()
