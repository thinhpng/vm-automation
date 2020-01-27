import argparse
import logging
import random
import threading
import time
import multiprocessing

try:
    import support_functions
    import vm_functions
except ModuleNotFoundError:
    print('Unable to import support_functions and/or vm_functions')
    exit(1)


# Parse command line arguments
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
main_options.add_argument('--info', default=1, choices=[1, 0], type=int, nargs='?',
                          help='Show file hash and links to VirusTotal and Google search (default: %(default)s)')
main_options.add_argument('--threads', default=2, choices=['vms', 'cores', 1, 2, 3, 4], nargs='?',
                          help='Not used yet')

guests_options = parser.add_argument_group('Guests options')
guests_options.add_argument('--ui', default='gui', choices=['gui', 'headless'], nargs='?',
                            help='Start VMs in GUI or headless mode (default: %(default)s)')
guests_options.add_argument('--login', default='user', type=str, nargs='?',
                            help='Login for guest OS (default: %(default)s)')
guests_options.add_argument('--password', default='P@ssw0rd', type=str, nargs='?',
                            help='Password for guest OS (default: %(default)s)')
guests_options.add_argument('--remote_folder', default='desktop', choices=['desktop', 'downloads', 'documents', 'temp'],
                            type=str, nargs='?',
                            help='Destination folder in guest OS to place file. (default: %(default)s)')
guests_options.add_argument('--network', default='keep', choices=['on', 'off', 'keep'], nargs='?',
                            help='State of guest OS network (default: %(default)s)')
guests_options.add_argument('--resolution', default='1920 1080 32', type=str, nargs='?',
                            help='Screen resolution for guest OS. Can be set to "random" (default: %(default)s)')
guests_options.add_argument('--pre', default=None, type=str, nargs='?',
                            help='Script to run before main file (default: %(default)s)')
guests_options.add_argument('--post', default=None, type=str, nargs='?',
                            help='Script to run after main file (default: %(default)s)')

args = parser.parse_args()
# Main options
filename = args.file[0]
vms_list = args.vms
snapshots_list = args.snapshots
threads = args.threads
timeout = args.timeout
vm_pre_exec = args.pre
vm_post_exec = args.post
ui = args.ui
vm_login = args.login
vm_password = args.password
remote_folder = args.remote_folder
vm_network_state = args.network
vm_resolution = args.resolution
# support_functions options
show_info = args.info
# vm_functions options
vm_functions.vboxmanage_path = args.vboxmanage

logging.info(f'VirtualBox version: {vm_functions.vm_version()[1].rstrip()}; Script version: 0.6.1')
logging.info(f'VMs: {vms_list}; Snapshots: {snapshots_list}\n')
result = support_functions.file_info(filename, show_info)
if result != 0:
    logging.error('Error while processing file. Exiting.')
    exit(1)


# Main routines
def main_routine(vm, snapshots_list):
    for snapshot in snapshots_list:
        task_name = f'{vm}_{snapshot}'
        logging.info(f'{vm}({snapshot}): Task started')

        # Stop VM, restore snapshot, start VM
        vm_functions.vm_stop(vm)
        time.sleep(3)
        result = vm_functions.vm_restore(vm, snapshot)
        # If we were unable to restore snapshot - continue to next one
        if result[0] != 0:
            logging.error(f'Unable to restore VM {vm} to snapshot {snapshot}. VM will be skipped.')
            vm_functions.vm_stop(vm)
            continue

        time.sleep(3)
        result = vm_functions.vm_start(vm)
        # If we were unable to start VM - continue to next one
        if result[0] != 0:
            logging.error(f'Unable to start VM {vm}. VM will be skipped.')
            continue

        # Wait for VM
        time.sleep(7)

        # Set guest network state
        result = vm_functions.vm_network(vm, vm_network_state)
        if result[0] != 0:
            vm_functions.vm_stop(vm)
            continue

        # Set guest resolution
        if vm_resolution == 'random':
            resolutions = ['1920 1080 32', '1920 1200 32', '2560 1440 32', '3840 2160 32']
            random_resolution = random.choice(resolutions)
            vm_functions.vm_set_resolution(vm, random_resolution)
        else:
            vm_functions.vm_set_resolution(vm, vm_resolution)

        # Run pre exec script
        if vm_pre_exec:
            vm_functions.vm_exec(vm, vm_login, vm_password, vm_pre_exec)
        else:
            logging.debug('Pre exec is not set.')

        # Randomize filename
        random_filename = support_functions.randomize_filename(vm_login, filename, remote_folder)

        # Upload file to VM, check if file exist and execute
        result = vm_functions.vm_upload(vm, vm_login, vm_password, filename, random_filename)
        if result[0] != 0:
            vm_functions.vm_screenshot(vm, task_name)
            vm_functions.vm_stop(vm)
            continue
        vm_functions.vm_screenshot(vm, task_name)

        # Check if file exist on VM
        result = vm_functions.vm_file_stat(vm, vm_login, vm_password, random_filename)
        if result[0] != 0:
            vm_functions.vm_screenshot(vm, task_name)
            vm_functions.vm_stop(vm)
            continue
        vm_functions.vm_screenshot(vm, task_name)

        # Run file
        result = vm_functions.vm_exec(vm, vm_login, vm_password, random_filename)
        if result[0] != 0:
            vm_functions.vm_screenshot(vm, task_name)
            vm_functions.vm_stop(vm)
            continue

        vm_functions.vm_screenshot(vm, task_name)
        logging.debug(f'Waiting for {timeout / 2} seconds...')
        time.sleep(timeout / 2)
        vm_functions.vm_screenshot(vm, task_name)
        logging.debug(f'Waiting for {timeout / 2} seconds...')
        time.sleep(timeout / 2)
        vm_functions.vm_screenshot(vm, task_name)

        # Run post exec script
        if vm_post_exec:
            vm_functions.vm_exec(vm, vm_login, vm_password, vm_post_exec)
        else:
            logging.debug('Post exec is not set.')

        vm_functions.vm_screenshot(vm, task_name)

        # Stop VM, restore snapshot
        vm_functions.vm_stop(vm)
        vm_functions.vm_restore(vm, snapshot)
        logging.info(f'{vm}({snapshot}): Task finished')


# If vms_list is set to 'all', obtain list of all available VMs and use them
if 'all' in vms_list:
    vms_list = vm_functions.list_vms()

if 'all' in snapshots_list:
    snapshots_autodetect = True
else:
    snapshots_autodetect = False

# Start threads
for vm in vms_list:
    if snapshots_autodetect:
        logging.debug('Snapshots list will be obtained from VM information.')
        snapshots_list = vm_functions.list_snapshots(vm)
        if snapshots_list[0] == 0:
            snapshots_list = snapshots_list[1]
        else:
            logging.error(f'Unable to get list of snapshots for VM {vm}. Skipping.')
            continue
    try:
        t = threading.Thread(target=main_routine, args=(vm, snapshots_list))
        t.start()
        time.sleep(5)  # Delay before starting next VM
    except (KeyboardInterrupt, SystemExit):
        raise
