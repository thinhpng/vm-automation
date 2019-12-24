import logging
import subprocess
import time


if __name__ == "__main__":
    print('This script only contains functions and cannot be called directly. See "demo.py" for usage example.')
    exit(1)


# Wrapper for vboxmanage command
def vboxmanage(cmd):
    cmd = f'{vboxmanage_path} {cmd}'.split()
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, text=True)
        return [result.returncode, result.stdout, result.stderr]
    except FileNotFoundError:
        logging.critical(f'Vboxmanage path is incorrect. Exiting.')
        exit()


# List virtual machines
def list_vms(state):
    if state == 'all':
        result = vboxmanage('list vms --sorted')
    elif state == 'running':
        result = vboxmanage('list runningvms --sorted')
    else:
        logging.error('VM state must be either "all" or "running".')
        pass
    return result[0], result[1], result[2]


# VirtualBox version
def vm_version():
    result = vboxmanage('--version')
    return result[0], result[1], result[2]


# Start virtual machine
def vm_start(vm, snapshot, **kwargs):
    if vm_ui not in ['gui', 'headless']:
        logging.error(f'{vm}({snapshot}): Unknown --type set for VM. Exiting.')
        exit(1)
    logging.info(f'{vm}({snapshot}): Starting VM')
    result = vboxmanage(f'startvm {vm} --type {vm_ui}')
    if result[0] == 0:
        logging.info(f'{vm}({snapshot}): VM started')
        time.sleep(5)  # Just to make sure VM is responsive
    else:
        logging.error(f'{vm}({snapshot}): Error while starting VM. Code: {result[0]}')
        logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')
    return result[0]


# Stop virtual machine
def vm_stop(vm, snapshot):
    logging.info(f'{vm}({snapshot}): Stopping VM')
    result = vboxmanage(f'controlvm {vm} poweroff')
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
    return result[0]


# Change network link state
def vm_network(vm, snapshot, link_state):
    if link_state == 'keep':
        logging.debug(f'{vm}({snapshot}): Keeping original network state')
        return 0
    elif link_state in ['on', 'off']:
        logging.info(f'{vm}({snapshot}): Setting network parameters to {link_state}')
        result = vboxmanage(f'controlvm {vm} setlinkstate1 {link_state}')
        if result[0] == 0:
            logging.debug(f'{vm}({snapshot}): Network state changed')
        else:
            logging.error(f'{vm}({snapshot}): Unable to change network state. Code: {result[0]}')
            logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')
        return result[0]
    else:
        logging.error(f'{vm}({snapshot}): link_state should be "on", "off" or "keep"')
        return 1


# Control screen resolution
def vm_set_resolution(vm, snapshot, screen_resolution):
    logging.info(f'{vm}({snapshot}): Changing screen resolution for VM')
    result = vboxmanage(f'controlvm {vm} setvideomodehint {screen_resolution}')
    if result[0] == 0:
        logging.debug(f'{vm}({snapshot}): Screen resolution changed')
    else:
        logging.error(f'{vm}({snapshot}): Unable to change screen resolution. Code: {result[0]}')
        logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')


# Execute file/command on VM
def vm_exec(vm, snapshot, username, password, remote_file):
    logging.info(f'{vm}({snapshot}): Executing file {remote_file}')
    _ = 0
    while _ < timeout:
        result = vboxmanage(
            f'guestcontrol {vm} --username {username} --password {password} start {remote_file}')
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


# Get information about file on VM
def vm_file_stat(vm, snapshot, username, password, remote_file):
    logging.debug(f'{vm}({snapshot}): Checking if file {remote_file} exist on VM')
    result = vboxmanage(f'guestcontrol {vm} --username {username} --password {password} start {remote_file}')
    if result[0] == 0:
        logging.debug(f'{vm}({snapshot}): File exist')
    else:
        logging.error(f'{vm}({snapshot}): File does not exist on VM {result[0]}')


# Upload file to VM
def vm_upload(vm, snapshot, username, password, local_file, remote_file):
    _ = 0
    while _ < timeout:
        logging.info(f'{vm}({snapshot}): Uploading file {local_file} as {remote_file} to VM')
        result = vboxmanage(
            f'guestcontrol {vm} --username {username} --password {password} copyto {local_file} {remote_file}')
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
        vm_stop(vm, snapshot)
        exit()


# Upload and execute file on VM
def vm_upload_exec(vm, snapshot, username, password, local_file, remote_file):
    vm_upload(vm, snapshot, username, password, local_file, remote_file)
    vm_file_stat(vm, snapshot, username, password, remote_file)
    vm_exec(vm, snapshot, username, password, remote_file)


# Download file from VM
def vm_download(vm, snapshot, username, password, local_file, remote_file):
    logging.info(f'{vm}({snapshot}): Downloading file {remote_file} from VM as {local_file}')
    result = vboxmanage(
        f'guestcontrol {vm} --username {username} --password {password} copyfrom {remote_file} {local_file}')
    if result[0] == 0:
        logging.debug(f'{vm}({snapshot}): File downloaded')
    else:
        logging.error(f'{vm}({snapshot}): Error while downloading file. Code: {result[0]}')
        logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')


# Take screenshot
def vm_screenshot(vm, snapshot, image_index=1):
    screenshot_name = f'{vm}_{snapshot}_{image_index}.png'
    logging.info(f'{vm}({snapshot}): Taking screenshot {screenshot_name}')
    result = vboxmanage(f'controlvm {vm} screenshotpng {screenshot_name}')
    if result[0] == 0:
        logging.debug(f'{vm}({snapshot}): Screenshot created')
    else:
        logging.error(f'{vm}({snapshot}): Unable to take screenshot')
        logging.debug(f'{vm}({snapshot}): stderr: {result[2]}')
    image_index += 1
    return image_index
