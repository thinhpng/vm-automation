import argparse
import logging
import random
import threading
import time
import os

script_version = '0.8'

try:
    import support_functions
    import vm_functions
except ModuleNotFoundError:
    print('Unable to import support_functions and/or vm_functions. Exiting.')
    exit(1)

# Parse command line arguments
parser = argparse.ArgumentParser(prog='vm-automation')

required_options = parser.add_argument_group('Required options')
required_options.add_argument('file', type=str, nargs='+', help='Path to file')
required_options.add_argument('--vms', '-v', type=str, nargs='*', required=True,
                   help='Space-separated list of VMs to use')
required_options.add_argument('--snapshots', '-s', type=str, nargs='*', required=True,
                              help='Space-separated list of snapshots to use')

main_options = parser.add_argument_group('Main options')
main_options.add_argument('--vboxmanage', default='vboxmanage', type=str, nargs='?',
                          help='Path to vboxmanage binary (default: %(default)s)')
main_options.add_argument('--timeout', default=60, type=int, nargs='?',
                          help='Timeout in seconds for both commands and VM (default: %(default)s)')
main_options.add_argument('--info', default=1, choices=[1, 0], type=int, nargs='?',
                          help='Show file hash and links to VirusTotal and Google search (default: %(default)s)')
main_options.add_argument('--threads', default=2, choices=range(9), type=int, nargs='?',
                          help='Number of concurrent threads to run (0=number of VMs, default: %(default)s)')
main_options.add_argument('--verbosity', default='info', choices=['debug', 'info', 'error'], type=str, nargs='?',
                          help='Log verbosity level (default: %(default)s)')
main_options.add_argument('--log', default='console', type=str, nargs='?',
                          help='Path to log file (default: %(default)s)')

guests_options = parser.add_argument_group('Guests options')
guests_options.add_argument('--ui', default='gui', choices=['gui', 'headless'], nargs='?',
                            help='Start VMs in GUI or headless mode (default: %(default)s)')
guests_options.add_argument('--login', default='user', type=str, nargs='?',
                            help='Login for guest OS (default: %(default)s)')
guests_options.add_argument('--password', default='12345678', type=str, nargs='?',
                            help='Password for guest OS (default: %(default)s)')
guests_options.add_argument('--remote_folder', default='desktop', choices=['desktop', 'downloads', 'documents', 'temp'],
                            type=str, nargs='?',
                            help='Destination folder in guest OS to place file. (default: %(default)s)')
guests_options.add_argument('--uac_fix', default=0, choices=[0, 1], type=int,
                            nargs='?', help='Fix for files with UAC elevation (default: %(default)s)')
guests_options.add_argument('--uac_parent', default='C:\\Windows\\Explorer.exe', type=str,
                            nargs='?', help='Path for parent app, which will start main file (default: %(default)s)')
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
verbosity = args.verbosity
log = args.log

# support_functions options
show_info = args.info

# vm_functions options
vm_functions.vboxmanage_path = args.vboxmanage
vm_functions.ui = args.ui
vm_functions.timeout = timeout

# VM options
vm_pre_exec = args.pre
vm_post_exec = args.post
vm_login = args.login
vm_password = args.password
remote_folder = args.remote_folder
uac_fix = args.uac_fix
uac_parent = args.uac_parent
vm_network_state = args.network
vm_resolution = args.resolution

# Logging options
if log == 'none':
    logging.disable()
elif verbosity in ['error', 'info', 'debug']:
    log_levels = {'error': logging.ERROR,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}
    if log == 'console':
        vm_functions.logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=log_levels[verbosity])
    else:
        vm_functions.logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=log_levels[verbosity],
                                         filename=log, filemode='a')
    vm_functions.logger = logging.getLogger('vm-automation')


# Show general info
def show_info():
    logging.info(f'Script version: {script_version}')
    logging.info(f'VirtualBox version: {vm_functions.virtualbox_version(strip_newline=1)[1]}\n')

    logging.info(f'VMs: {vms_list}')
    logging.info(f'Snapshots: {snapshots_list}\n')
    result = support_functions.file_info(filename, show_info)
    if result != 0:
        logging.error('Error while processing file. Exiting.')
        exit(1)


# Function to take screenshot on guest OS
def take_screenshot(vm, task_name):
    screenshot_index = 1
    while screenshot_index < 10000:
        screenshot_index_zeros = str(screenshot_index).zfill(4)
        screenshot_name_num = f'{task_name}_{screenshot_index_zeros}.png'
        if os.path.isfile(screenshot_name_num):
            screenshot_index += 1
        else:
            vm_functions.vm_screenshot(vm, screenshot_name_num)
            break


# Main routines
def main_routine(vm, snapshots_list):
    for snapshot in snapshots_list:
        task_name = f'{vm}_{snapshot}'
        logging.info(f'{task_name}: Task started')

        # Stop VM, restore snapshot, start VM
        vm_functions.vm_stop(vm, ignore_status_error=1)
        time.sleep(3)
        result = vm_functions.vm_snapshot_restore(vm, snapshot)
        # If we were unable to restore snapshot - continue to next snapshot/VM
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
            resolutions = ['1280 1024 32', '1920 1080 32', '1920 1200 32', '2560 1440 32', '3840 2160 32']
            random_resolution = random.choice(resolutions)
            vm_functions.vm_set_resolution(vm, random_resolution)
        else:
            vm_functions.vm_set_resolution(vm, vm_resolution)

        # Run pre exec script
        if vm_pre_exec:
            vm_functions.vm_exec(vm, vm_login, vm_password, vm_pre_exec)
            take_screenshot(vm, task_name)
        else:
            logging.debug('Pre exec is not set.')

        # Set path to file on guest OS
        remote_file_path = support_functions.randomize_filename(vm_login, filename, remote_folder)

        # Upload file to VM, check if file exist and execute
        result = vm_functions.vm_upload(vm, vm_login, vm_password, filename, remote_file_path)
        if result[0] != 0:
            take_screenshot(vm, task_name)
            vm_functions.vm_stop(vm)
            continue
        take_screenshot(vm, task_name)

        # Check if file exist on VM
        result = vm_functions.vm_file_stat(vm, vm_login, vm_password, remote_file_path)
        if result[0] != 0:
            take_screenshot(vm, task_name)
            vm_functions.vm_stop(vm)
            continue
        take_screenshot(vm, task_name)

        # Run file
        result = vm_functions.vm_exec(vm, vm_login, vm_password, remote_file_path, uac_fix=uac_fix,
                                      uac_parent=uac_parent)
        if result[0] != 0:
            take_screenshot(vm, task_name)
            vm_functions.vm_stop(vm)
            continue

        take_screenshot(vm, task_name)
        logging.debug(f'Waiting for {timeout / 2} seconds...')
        time.sleep(timeout / 2)
        take_screenshot(vm, task_name)
        logging.debug(f'Waiting for {timeout / 2} seconds...')
        time.sleep(timeout / 2)
        take_screenshot(vm, task_name)

        # Run post exec script
        if vm_post_exec:
            vm_functions.vm_exec(vm, vm_login, vm_password, vm_post_exec)
            take_screenshot(vm, task_name)
        else:
            logging.debug('Post exec is not set.')

        # Stop VM, restore snapshot
        vm_functions.vm_stop(vm)
        vm_functions.vm_snapshot_restore(vm, snapshot)
        logging.info(f'{task_name}: Task finished')


if 'all' in vms_list:
    # If vms_list is set to 'all', obtain list of all available VMs and use them
    vms_list = vm_functions.list_vms()

# Autodetect snapshots
if 'all' in snapshots_list:
    snapshots_autodetect = True
else:
    snapshots_autodetect = False

# Number of concurrent threads
if threads == 0:
    threads = len(vms_list)
    logging.debug(f'Threads count is set to number of VMs: {threads}')
else:
    logging.debug(f'Threads count is set to {threads}')

show_info()

# Start threads
for vm in vms_list:
    # Limit number of concurrent threads
    while threading.active_count() - 1 >= threads:
        time.sleep(3)

    if snapshots_autodetect:
        logging.debug('Snapshots list will be obtained from VM information.')
        snapshots_list = vm_functions.list_snapshots(vm)
        if snapshots_list[0] == 0:
            snapshots_list = snapshots_list[1]
        else:
            logging.error(f'Unable to get list of snapshots for VM "{vm}". Skipping.')
            continue

    try:
        t = threading.Thread(target=main_routine, args=(vm, snapshots_list))
        t.name = f'{vm}_{snapshots_list}'
        t.start()
        time.sleep(5)  # Delay before starting next VM
    except (KeyboardInterrupt, SystemExit):
        raise
