import argparse
import logging
import os
import threading
import time

script_version = '0.10.1'

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
main_options.add_argument('--delay', default=7, type=int, nargs='?',
                          help='Delay in seconds before/after starting VMs (default: %(default)s)')
main_options.add_argument('--threads', default=2, choices=range(9), type=int, nargs='?',
                          help='Number of concurrent threads to run (0=number of VMs, default: %(default)s)')
main_options.add_argument('--verbosity', default='info', choices=['debug', 'info', 'error', 'off'], type=str, nargs='?',
                          help='Log verbosity level (default: %(default)s)')
main_options.add_argument('--debug', action='store_true',
                          help='Print all messages. Alias for "--verbosity debug" (default: %(default)s)')
main_options.add_argument('--log', default=None, type=argparse.FileType('w'), nargs='?',
                          help='Path to log file (default: %(default)s) (console)')
main_options.add_argument('--report', action='store_true',
                          help='Generate html report (default: %(default)s)')
main_options.add_argument('--record', action='store_true',
                          help='Record guest\' OS screen (default: %(default)s)')
main_options.add_argument('--pcap', action='store_true',
                          help='Enable recording of VM\'s traffic (default: %(default)s)')
main_options.add_argument('--memdump', action='store_true',
                          help='Dump memory VM (default: %(default)s)')

guests_options = parser.add_argument_group('Guests options')
guests_options.add_argument('--ui', default='gui', choices=['1', '0', 'gui', 'headless'], nargs='?',
                            help='Start VMs in GUI or headless mode (default: %(default)s)')
guests_options.add_argument('--login', '--user', default='user', type=str, nargs='?',
                            help='Login for guest OS (default: %(default)s)')
guests_options.add_argument('--password', default='12345678', type=str, nargs='?',
                            help='Password for guest OS (default: %(default)s)')
guests_options.add_argument('--remote_folder', default='desktop', choices=['desktop', 'downloads', 'documents', 'temp'],
                            type=str, nargs='?',
                            help='Destination folder in guest OS to place file. (default: %(default)s)')
guests_options.add_argument('--uac_parent', default='C:\\Windows\\Explorer.exe', type=str,
                            nargs='?', help='Path for parent app, which will start main file (default: %(default)s)')
guests_options.add_argument('--network', default=None, choices=['on', 'off'], nargs='?',
                            help='State of network adapter of guest OS (default: %(default)s)')
guests_options.add_argument('--resolution', default=None, type=str, nargs='?',
                            help='Screen resolution for guest OS. Can be set to "random" (default: %(default)s)')
guests_options.add_argument('--mac', default=None, type=str, nargs='?',
                            help='Set MAC address for guest OS. Can be set to "random" (default: %(default)s)')
guests_options.add_argument('--get_file', default=None, type=str, nargs='?',
                            help='Get specific file from guest OS before stopping VM (default: %(default)s)')

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
delay = args.delay
verbosity = args.verbosity
debug = args.debug
log = args.log
report = args.report
record = args.record
pcap = args.pcap
memdump = args.memdump

# vm_functions options
vm_functions.vboxmanage_path = args.vboxmanage
ui = args.ui
vm_functions.timeout = timeout

# VM options
vm_pre_exec = args.pre
vm_post_exec = args.post
vm_login = args.login
vm_password = args.password
remote_folder = args.remote_folder
uac_parent = args.uac_parent
vm_network_state = args.network
vm_resolution = args.resolution
vm_mac = args.mac
vm_get_file = args.get_file

# Some VirtualBox commands require full path to file
cwd = os.getcwd()

# Logging options
if debug:
    verbosity = 'debug'
if log == 'off':
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
    result = support_functions.file_info(filename)
    if result[0] != 0:
        logging.error('Error while processing file. Exiting.')
        exit(1)
    return result[1], result[2], result[3]


# Function to take screenshot on guest OS
def take_screenshot(vm, task_name):
    screenshot_index = 1
    while screenshot_index < 10000:
        screenshot_index_zeros = str(screenshot_index).zfill(4)
        if report:
            screenshot_name_num = f'reports/{sha256}/{task_name}_{screenshot_index_zeros}.png'
        else:
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

        # Create directory for report
        if report:
            os.makedirs(f'reports/{sha256}', mode=0o444, exist_ok=True)

        # Stop VM, restore snapshot
        vm_functions.vm_stop(vm, ignore_status_error=1)
        time.sleep(delay / 2)
        result = vm_functions.vm_snapshot_restore(vm, snapshot, ignore_status_error=1)
        if result[0] != 0:
            # If we were unable to restore snapshot - continue to the next snapshot/VM
            logging.error(f'Unable to restore VM "{vm}" to snapshot "{snapshot}". Skipping.')
            vm_functions.vm_stop(vm, ignore_status_error=1)
            continue
        # Change MAC address
        if vm_mac:
            vm_functions.vm_set_mac(vm, vm_mac)
        # Dump traffic
        if pcap:
            if vm_network_state == 'off':
                logging.warning('Traffic dump enabled, but network state is set to \'off\'.')
            if report:
                pcap_file = f'{cwd}/reports/{sha256}/{vm}_{snapshot}.pcap'
            else:
                pcap_file = f'{cwd}/{vm}_{snapshot}.pcap'
            vm_functions.vm_pcap(vm, pcap_file)

        # Start VM
        time.sleep(delay / 2)
        result = vm_functions.vm_start(vm, ui)
        if result[0] != 0:
            # If we were unable to start VM - continue to the next one
            logging.error(f'Unable to start VM "{vm}". Skipping.')
            continue

        # Wait for VM
        time.sleep(delay)

        # Set guest network state
        result = vm_functions.vm_network(vm, vm_network_state)
        if result[0] != 0:
            vm_functions.vm_stop(vm)
            continue

        # Set guest resolution
        vm_functions.vm_set_resolution(vm, vm_resolution)

        # Start screen recording
        if record:
            if report:
                recording_name = f'{cwd}/reports/{sha256}/{vm}_{snapshot}.webm'
            else:
                recording_name = f'{cwd}/{vm}_{snapshot}.webm'
            recording_name = support_functions.normalize_path(recording_name)
            vm_functions.vm_record(vm, recording_name)

        # Run pre exec script
        if vm_pre_exec:
            vm_functions.vm_exec(vm, vm_login, vm_password, vm_pre_exec, uac_parent=uac_parent)
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

        # Check if file exist on VM
        result = vm_functions.vm_file_stat(vm, vm_login, vm_password, remote_file_path)
        if result[0] != 0:
            take_screenshot(vm, task_name)
            vm_functions.vm_stop(vm)
            continue
        take_screenshot(vm, task_name)

        # Run file
        result = vm_functions.vm_exec(vm, vm_login, vm_password, remote_file_path, uac_parent=uac_parent)
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

        # Check for file at the end of task
        result = vm_functions.vm_file_stat(vm, vm_login, vm_password, remote_file_path)
        if result[0] != 0:
            logging.info('Original file does not exists anymore (melted or removed by AV).')

        # Run post exec script
        if vm_post_exec:
            vm_functions.vm_exec(vm, vm_login, vm_password, vm_post_exec, uac_parent=uac_parent)
            take_screenshot(vm, task_name)
        else:
            logging.debug('Post exec is not set.')

        # Get file from guest
        if vm_get_file:
            # Normalize path and extract file name
            src_path = support_functions.normalize_path(vm_get_file)
            src_filename = os.path.basename(src_path)
            if report:
                # Place in reports directory
                dst_file = f'{cwd}/reports/{sha256}/{src_filename}'
            else:
                # Place in current dir
                dst_file = f'{cwd}/{src_filename}'
            # Download file
            vm_functions.vm_copyfrom(vm, vm_login, vm_password, src_path, dst_file)

        # Stop recording
        if record:
            vm_functions.vm_record_stop(vm)

        # Dump VM memory
        if memdump:
            if report:
                memdump_file = f'{cwd}/reports/{sha256}/{vm}_{snapshot}.dmp'
            else:
                memdump_file = f'{cwd}/{vm}_{snapshot}.dmp'
            vm_functions.vm_memdump(vm, memdump_file)

        # Stop VM
        vm_functions.vm_stop(vm)

        # Save html report as ./reports/<file_hash>/index.html
        if report:
            support_functions.html_report(vm, snapshot, filename, file_size, sha256, md5, timeout, vm_network_state)

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
    if threads > len(vms_list):
        logging.warning(f'Number of concurrent threads is larger then number of available VMs ({len(vms_list)}).')
        threads = len(vms_list)
    logging.debug(f'Threads count is set to {threads}')

# Show file information
sha256, md5, file_size = show_info()

# Start threads
for vm in vms_list:
    # Limit number of concurrent threads
    while threading.active_count() - 1 >= threads:
        time.sleep(delay / 2)

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
        time.sleep(delay)  # Delay before starting next VM
    except (KeyboardInterrupt, SystemExit):
        raise
