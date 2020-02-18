import hashlib
import logging
import os
import random
import re
import string

if __name__ == "__main__":
    print('This script only contains functions and cannot be called directly. See "demo_cli.py" for usage example.')
    exit(1)


# Show info about file
def file_info(file, show_info=True):
    file = ''.join(file)
    logging.info(f'File: "{file}"')

    # Check if file exists
    if not os.path.isfile(file):
        logging.error(f'File "{file}" does not exists.')
        return 1

    # Print hash and links
    if show_info:
        file_hash = hashlib.sha256()
        block_size = 65536
        with open(file, 'rb') as f:
            fb = f.read(block_size)
            while len(fb) > 0:
                file_hash.update(fb)
                fb = f.read(block_size)
        sha256sum = file_hash.hexdigest()
        logging.info(f'sha256: {sha256sum}')
        logging.info(f'Search VT: https://www.virustotal.com/gui/file/{sha256sum}/detection')
        logging.info(f'Search Google: https://www.google.com/search?q={sha256sum}\n')
    return 0


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


def set_log_level(func):

    func()
