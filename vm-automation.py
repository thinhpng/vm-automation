import argparse
import hashlib
import logging
import os
import random
import re
import string
import subprocess
import threading
import time

# Get command line arguments
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
# main_options.add_argument('--threads', default=2, type=int, nargs='?',
#                           help='Number of threads (VMs) to start simultaneously (default: %(default)s)')

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
guests_options.add_argument('--resolution', default='1024 768 32', type=str, nargs='?',
                            help='Screen resolution for guest OS (default: %(default)s)')
guests_options.add_argument('--pre', default=False, type=str, nargs='?',
                            help='Script to run before main file (default: %(default)s)')
guests_options.add_argument('--post', default=False, type=str, nargs='?',
                            help='Script to run after main file (default: %(default)s)')

# Set options
args = parser.parse_args()
filename = args.file
vms_list = args.vms
snapshots_list = args.snapshots
vboxmanage_path = args.vboxmanage
vm_ui = args.ui
vm_login = args.login
vm_password = args.password
vm_remote_folder = args.remote_folder
vm_network_state = args.network
vm_resolution = args.resolution
vm_pre_exec = args.pre
vm_post_exec = args.post
timeout = args.timeout
show_hash = args.hash
show_links = args.links
# threads = args.threads

# Logging options
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)
logger = logging.getLogger('vm-automation')


# Process file
def process_file(file):
    file = ''.join(file)
    logging.info(f'File: {file}\n')

    # Check if file exists
    if not os.path.isfile(file):
        logging.error('File does not exists. Exiting.')
        exit()

    # Print hash and links
    if show_hash or show_links:
        file_hash = hashlib.sha256()
        block_size = 65536
        with open(file, 'rb') as f:
            fb = f.read(block_size)
            while len(fb) > 0:
                file_hash.update(fb)
                fb = f.read(block_size)
        sha256sum = file_hash.hexdigest()
        if show_hash:
            logging.info(f'sha256: {sha256sum}')
        if show_links:
            logging.info(f'Search VT: https://www.virustotal.com/gui/file/{sha256sum}/detection')
            logging.info(f'Search Google: https://www.google.com/search?q={sha256sum}\n')
    time.sleep(1)


def randomize_filename(file):
    local_file_extension = re.findall('\\.\\w+$', file)
    if not local_file_extension:
        logging.debug('Unable to obtain file extension. Assuming .exe')
        local_file_extension = '.exe'
    random_name = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(4, 20)))
    if string.ascii_lowercase(vm_remote_folder) == 'desktop':

    elif string.ascii_lowercase(vm_remote_folder) == 'downloads':

    elif string.ascii_lowercase(vm_remote_folder) == 'temp':

    else:

    random_filename = vm_remote_folder + random_name + ''.join(local_file_extension)
    return random_filename


# Wrapper for vboxmanage command
def vboxmanage(cmd):
    cmd = f'{vboxmanage_path} {cmd}'.split()
    logging.debug(f'Executing command: {cmd}')
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, text=True)
        return [result.returncode, result.stdout, result.stderr]
    except FileNotFoundError:
        logging.critical(f'Vboxmanage path is incorrect. Exiting.')
        exit()


# VirtualBox version
def vm_version():
    result = vboxmanage('--version')
    return result[1].rstrip()


# Start virtual machine
def vm_start(vm, snapshot):
    if vm_ui not in ['gui', 'headless']:
        logging.error(f'{vm}({snapshot}): Unknown --type set for VM. Exiting.')
        exit()
    logging.info(f'{vm}({snapshot}): Starting VM')
    result = vboxmanage(f'startvm {vm} --type {vm_ui}')
    if result[0] == 0:
        logging.info(f'{vm}({snapshot}): VM started')
        time.sleep(5)  # Just to make sure VM is responsive
    else:
        logging.error(f'{vm}({snapshot}): Error while starting VM. Code: {result[0]}')
        logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')
        exit()


# Stop virtual machine
def vm_stop(vm, snapshot):
    logging.info(f'{vm}({snapshot}): Stopping VM')
    result = vboxmanage(f'controlvm {vm_name} poweroff')
    if result[0] == 0:
        logging.debug(f'{vm}({snapshot}): VM stopped')
        time.sleep(3)
    elif result[0] == 1:
        logging.debug(f'{vm}({snapshot}): VM not running')
    else:
        logging.error(f'{vm}({snapshot}): Unknown error: {result[0]}')
        logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')


# Restore snapshot for virtual machine
def vm_restore(vm, snapshot):
    logging.info(f'{vm}({snapshot}): Restoring snapshot')
    result = vboxmanage(f'snapshot {vm} restore {snapshot}')
    if result[0] == 0:
        logging.debug(f'{vm}({snapshot}): Snapshot restored')
        time.sleep(3)
    else:
        logging.error(f'{vm}({snapshot}): Error while restoring snapshot. Code: {result[0]}')
        logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')


# Change network link state
def vm_network(vm, snapshot, link_state):
    if link_state == 'keep':
        logging.debug(f'{vm}({snapshot}): Keeping original NIC state')
    elif link_state in ['on', 'off']:
        logging.info(f'{vm}({snapshot}): Setting network parameters to {link_state}')
        result = vboxmanage(f'controlvm {vm_name} setlinkstate1 {link_state}')
        if result[0] == 0:
            logging.debug(f'{vm}({snapshot}): NIC state changed')
        else:
            logging.error(f'{vm}({snapshot}): Unable to change NIC state. Code: {result[0]}')
            logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')
    else:
        logging.error(f'{vm}({snapshot}): link_state should be "on", "off" or "keep"')
        exit()


# Control screen resolution
def vm_set_resolution(vm, snapshot, screen_resolution):
    logging.info(f'{vm}({snapshot}): Changing screen resolution for VM')
    result = vboxmanage(f'controlvm {vm_name} setvideomodehint {screen_resolution}')
    if result[0] == 0:
        logging.debug(f'{vm}({snapshot}): Screen resolution changed')
    else:
        logging.error(f'{vm}({snapshot}): Unable to change screen resolution. Code: {result[0]}')
        logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')


# Execute file/command on VM
def vm_exec(vm, snapshot, username, password, remote_file):
    if not remote_file:
        logging.debug(f'{vm}({snapshot}): Remote file not set. Skipping.')
        pass

    print(f'remote_file: {remote_file}')
    logging.info(f'{vm}({snapshot}): Executing file {remote_file}')
    _ = 0
    while _ < timeout:
        result = vboxmanage(
            f'guestcontrol {vm_name} --username {username} --password {password} start {remote_file}')
        if result[0] == 0:
            logging.debug(f'{vm}({snapshot}): File executed successfully')
            break
        else:
            # Waiting for VM to start
            time.sleep(1)
            _ += 1
    if _ >= timeout:
        logging.error(f'{vm}({snapshot}): Timeout while executing file on VM')
        vm_stop(vm, snapshot)
        exit()


# Copy file to VM
def vm_copyto(vm, snapshot, username, password, local_file, remote_file):
    _ = 0
    while _ < timeout:
        logging.info(f'{vm}({snapshot}): Uploading file {local_file} as {remote_file} to VM')
        result = vboxmanage(
            f'guestcontrol {vm_name} --username {username} --password {password} copyto {local_file} {remote_file}')
        if result[0] == 0:
            logging.debug(f'{vm}({snapshot}): File uploaded')
            break
        else:
            logging.error(f'{vm}({snapshot}): Error while uploading file. Code: {result[0]}')
            logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')
    time.sleep(1)
    _ += 1
    if _ >= timeout:
        logging.error(f'{vm}({snapshot}): Timeout while waiting for VM')
        exit()


# Copy file from VM
def vm_copyfrom(vm, snapshot, username, password, local_file, remote_file):
    logging.info(f'{vm}({snapshot}): Downloading file {remote_file} from VM as {local_file}')
    result = vboxmanage(
        f'guestcontrol {vm_name} --username {username} --password {password} copyfrom {remote_file} {local_file}')
    if result[0] == 0:
        logging.debug(f'{vm}({snapshot}): File downloaded')
    else:
        logging.error(f'{vm}({snapshot}): Error while downloading file. Code: {result[0]}')
        logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')


# Take screenshot
def vm_screenshot(vm, snapshot, image_id=1):
    screenshot_name = f'{vm_name}_{snapshot}_{image_id}.png'
    logging.info(f'{vm}({snapshot}): Taking screenshot {screenshot_name}')
    result = vboxmanage(f'controlvm {vm_name} screenshotpng {screenshot_name}')
    if result[0] == 0:
        logging.debug(f'{vm}({snapshot}): Screenshot created')
    else:
        logging.error(f'{vm}({snapshot}): Unable to take screenshot')
        logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')
    image_id += 1
    return image_id


# Main routines
def main_routine(vm, snapshot):
    for snapshot_name in snapshots_list:
        logging.info(f'{vm}({snapshot}): Task started')

        # Stop VM, restore snapshot, start VM
        vm_stop(vm_name, snapshot_name)
        vm_restore(vm_name, snapshot_name)
        vm_start(vm_name, snapshot_name)

        # Set guest resolution
        vm_set_resolution(vm_name, snapshot_name, vm_resolution)

        # Set guest network state
        vm_network(vm_name, snapshot_name, vm_network_state)

        # Run pre exec script
        vm_exec(vm_name, snapshot_name, vm_login, vm_password, vm_pre_exec)

        # Upload file to VM; take screenshot; start file; take screenshot; sleep 2 seconds; take screenshot;
        # wait for {timeout/2} seconds; take screenshot; wait for {timeout/2} seconds; take screenshot
        remote_file = randomize_filename(filename)
        vm_copyto(vm_name, snapshot_name, vm_login, vm_password, filename, remote_file)
        screenshot = vm_screenshot(vm_name, snapshot_name)
        vm_exec(vm_name, snapshot_name, vm_login, vm_password, remote_file)
        screenshot = vm_screenshot(vm_name, snapshot_name, screenshot)
        time.sleep(2)
        screenshot = vm_screenshot(vm_name, snapshot_name, screenshot)
        time.sleep(timeout / 2)
        screenshot = vm_screenshot(vm_name, snapshot_name, screenshot)
        time.sleep(timeout / 2)
        vm_screenshot(vm_name, snapshot_name, screenshot)

        # Run post exec script
        vm_exec(vm_name, snapshot_name, vm_login, vm_password, vm_post_exec)

        # Stop VM, restore snapshot
        vm_stop(vm_name, snapshot_name)
        vm_restore(vm_name, snapshot_name)
        logging.info(f'{vm}({snapshot}): Task finished')


# Start
logging.info(f'VirtualBox version: {vm_version()}; Script version: 0.4\n')
logging.info(f'VMs: {vms_list}')
logging.info(f'Snapshots: {snapshots_list}\n')
process_file(filename)

# Start threads
for vm_name in vms_list:
    print(vm_name)
    t = threading.Thread(target=main_routine, args=(vm_name, snapshots_list))
    t.start()
    time.sleep(5)  # Delay before starting next VM
