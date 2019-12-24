import argparse
import logging
import threading
import time

import support_functions
import vm_functions

# Logging options
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)
logger = logging.getLogger('vm-automation')

# Parse command line args
parser = argparse.ArgumentParser(prog='vm-automation')

required_options = parser.add_argument_group('Required options')
required_options.add_argument('file', type=str, nargs='+', help='Path to file')
required_options.add_argument('--vms', type=str, nargs='*', required=True,
                              help='Space-separated list of virtual machines to use')
required_options.add_argument('--snapshots', type=str, nargs='*', required=True,
                              help='Space-separated list of snapshots to use')

main_options = parser.add_argument_group('Main options')
main_options.add_argument('--vboxmanage', default='vboxmanage', type=str, nargs='?',
                          help='Path to vboxmanage binary (default: %(default)s)')
main_options.add_argument('--timeout', default=60, type=int, nargs='?',
                          help='Timeout in seconds for both commands and VM (default: %(default)s)')
main_options.add_argument('--hash', default=1, choices=[1, 0], nargs='?',
                          help='Calculate and print hash for file (default: %(default)s)')
main_options.add_argument('--links', default=1, choices=[1, 0], nargs='?',
                          help='Show links to VirusTotal and Google search (default: %(default)s)')
main_options.add_argument('--threads', default=2, type=int, nargs='?',
                          help='Not used yet')

guests_options = parser.add_argument_group('Guests options')
guests_options.add_argument('--ui', default='gui', choices=['gui', 'headless'], nargs='?',
                            help='Start VMs in GUI or headless mode (default: %(default)s)')
guests_options.add_argument('--login', default='user', type=str, nargs='?',
                            help='Login for guest OS (default: %(default)s)')
guests_options.add_argument('--password', default='P@ssw0rd', type=str, nargs='?',
                            help='Password for guest OS (default: %(default)s)')
guests_options.add_argument('--remote_folder', default='Desktop', choices=['Desktop', 'Downloads', 'Temp'], type=str,
                            nargs='?', help='Destination folder in guest OS to place file. (default: %(default)s)')
guests_options.add_argument('--network', default='keep', choices=['on', 'off', 'keep'], nargs='?',
                            help='State of guest OS network (default: %(default)s)')
guests_options.add_argument('--resolution', default='1920 1080 24', type=str, nargs='?',
                            help='Screen resolution for guest OS (default: %(default)s)')
guests_options.add_argument('--pre', default=None, type=str, nargs='?',
                            help='Script to run before main file (default: %(default)s)')
guests_options.add_argument('--post', default=None, type=str, nargs='?',
                            help='Script to run after main file (default: %(default)s)')

# Set options
args = parser.parse_args()
filename = args.file[0]
vms_list = args.vms
snapshots_list = args.snapshots
vboxmanage_path = args.vboxmanage
vm_ui = args.ui
vm_login = args.login
vm_password = args.password
remote_folder = args.remote_folder
vm_network_state = args.network
vm_resolution = args.resolution
vm_pre_exec = args.pre
vm_post_exec = args.post
timeout = args.timeout
show_hash = args.hash
show_links = args.links
threads = args.threads


logging.info(f'VirtualBox version: {vm_functions.vm_version()}; Script version: 0.4.1\n')
logging.info(f'VMs: {vms_list}')
logging.info(f'Snapshots: {snapshots_list}\n')
support_functions.process_file(filename)


# Main routines
def main_routine(vm, snapshots_list):
    for snapshot in snapshots_list:
        logging.info(f'{vm}({snapshot}): Task started')

        # Stop VM, restore snapshot, start VM
        vm_functions.vm_stop(vm, snapshot)
        result = vm_functions.vm_restore(vm, snapshot)
        # If we were unable to restore snapshot - continue to next one
        if result != 0:
            print('vm_restore result != 0')
        result = vm_functions.vm_start(vm, snapshot)
        # If we were unable to start VM - continue to next one
        if result != 0:
            print('vm_start result != 0')

        # Set guest resolution
        vm_functions.vm_set_resolution(vm, snapshot, vm_resolution)

        # Set guest network state
        vm_functions.vm_network(vm, snapshot, vm_network_state)

        # Run pre exec script
        if vm_pre_exec:
            vm_functions.vm_exec(vm, snapshot, vm_login, vm_password, vm_pre_exec)
        else:
            logging.debug(f'{vm}({snapshot}): Pre exec is not set')

        # Upload file to VM; take screenshot; start file; take screenshot; sleep 2 seconds; take screenshot;
        # wait for {timeout/2} seconds; take screenshot; wait for {timeout/2} seconds; take screenshot
        random_filename = support_functions.randomize_filename(vm, snapshot, vm_login, filename, remote_folder)
        vm_functions.vm_upload_exec(vm, snapshot, vm_login, vm_password, filename, random_filename)
        screenshot = vm_functions.vm_screenshot(vm, snapshot)
        time.sleep(2)
        screenshot = vm_functions.vm_screenshot(vm, snapshot, screenshot)
        time.sleep(timeout / 2)
        screenshot = vm_functions.vm_screenshot(vm, snapshot, screenshot)
        time.sleep(timeout / 2)
        screenshot = vm_functions.vm_screenshot(vm, snapshot, screenshot)

        # Run post exec script
        if vm_post_exec:
            vm_functions.vm_exec(vm, snapshot, vm_login, vm_password, vm_post_exec)
        else:
            logging.debug(f'{vm}({snapshot}): Post exec is not set')

        # Stop VM, restore snapshot
        vm_functions.vm_stop(vm, snapshot)
        vm_functions.vm_restore(vm, snapshot)
        logging.info(f'{vm}({snapshot}): Task finished')


# Start threads
for vm in vms_list:
    t = threading.Thread(target=main_routine, args=(vm, snapshots_list))
    t.start()
    time.sleep(5)  # Delay before starting next VM
