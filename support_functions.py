import hashlib
import logging
import os
import random
import re
import string
import datetime

if __name__ == "__main__":
    print('This script only contains functions and cannot be called directly. See "demo_cli.py" for usage example.')
    exit(1)


def file_hash(file):
    file_hash_ = hashlib.sha256()
    block_size = 65536
    with open(file, 'rb') as f:
        fb = f.read(block_size)
        while len(fb) > 0:
            file_hash_.update(fb)
            fb = f.read(block_size)
    sha256sum = file_hash_.hexdigest()
    return sha256sum


# Show info about file
def file_info(file):
    file = ''.join(file)
    logging.info(f'File: "{file}"')

    # Check if file exists
    if not os.path.isfile(file):
        logging.error(f'File "{file}" does not exists.')
        return 1

    # Print hash and links
    sha256sum = file_hash(file)
    logging.info(f'sha256: {sha256sum}')
    logging.info(f'Search VT: https://www.virustotal.com/gui/file/{sha256sum}/detection')
    logging.info(f'Search Google: https://www.google.com/search?q={sha256sum}\n')
    return 0, sha256sum


def randomize_filename(login, file, destination_folder):
    # File name
    random_name = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(4, 20)))

    # File extension
    file_extension = re.search(r'\.\w+$', file).group()
    if not file_extension:
        logging.debug('Unable to obtain file extension. Assuming .exe')
        file_extension = '.exe'

    # Destination folder
    if destination_folder.lower() in ['desktop', 'downloads', 'documents']:
        destination_folder = f'C:\\Users\\{login}\\{destination_folder}\\'
    elif destination_folder.lower() == 'temp':
        destination_folder = f'C:\\Users\\{login}\\AppData\\Local\\Temp\\'
    else:
        logging.debug('Using custom remote_folder')

    random_filename = destination_folder + random_name + file_extension
    logging.debug(f'Remote file: "{random_filename}"')
    return random_filename


def html_report(vms_list, snapshots_list, filename, sha256, timeout, vm_network_state, reports_directory='reports'):
    # Set options and paths
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    destination_dir = reports_directory + '/' + sha256
    destination_file = destination_dir + '/index.html'

    # Create directory, if it does not exist
    os.makedirs(destination_dir, mode=0o444, exist_ok=True)

    # Content of html file
    html_template_header = f'''
    <!DOCTYPE html>
    <html>
    <title>Report</title>
    <body>
    <h3>File info:</h3>
    <table>
      <tr>
        <td><b>Filename:</b></td>
        <td>{filename}</td>
      </tr>
      <tr>
        <td><b>Sha256 hash:</b></td>
        <td>{sha256}</td>
      </tr>
      <tr>    
        <td><b>Scanned on:</b></td>
        <td>{time}</td>
      </tr>
      <tr>    
        <td><b>Timeout:</b></td>
        <td>{timeout} seconds</td>
      </tr>
      <tr>    
        <td><b>Network:</b></td>
        <td>{vm_network_state}</td>
      </tr>
    </table>
    <br>
    '''

    html_template_screenshots = ''
    for vm in vms_list:
        for snapshot in snapshots_list:
            html_template_screenshots += f'''<h3>VM:</b> {vm}, <b>Snapshot:</b> {snapshot}<h3>'''
            screenshots = os.listdir(destination_dir)
            for screenshot in screenshots:
                # Check if filename matches task name and have .png extension
                if re.search(rf'{vm}_{snapshot}_\d+\.png', screenshot):
                    print(f'{screenshot} matches pattern!')
                    html_template_screenshots += f'''
                    <a href="{screenshot}" target=_blank><img src="{screenshot}" width="320" high="240"></img></a>
                    '''
                else:
                    print(f'{screenshot} does not matches pattern!')

    html_template_footer = '</body></html>'

    # Write data to report file
    file_object = open(destination_file, 'w')
    file_object.write(html_template_header + html_template_screenshots + html_template_footer)

