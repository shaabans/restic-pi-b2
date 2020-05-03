import logging
import os
import psutil
import subprocess as sp
import config

b2_bucket = config.b2_bucket
os.environ['B2_ACCOUNT_ID'] = config.b2_account_id
os.environ['B2_ACCOUNT_KEY'] = config.b2_account_key
os.environ['RESTIC_PASSWORD'] = config.restic_password

logging.basicConfig(filename='restic.log',
                    format='%(asctime)s:%(levelname)s: %(message)s',
                    level=logging.DEBUG)

# Check if there is any running process that contains the given process
def is_running(process_name='restic'):
  # Iterate over the all the running process
  for proc in psutil.process_iter():
    try:
      # Check if process name contains the given name string.
      if process_name.lower() in proc.name().lower():
        logging.warning('Another Restic process is currently running, aboring.')
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
      pass
  return False

# Create name in the form of "b2:bucket:repo"
def get_full_repo_name(bucket_name, repo_name):
  return 'b2:' + bucket_name + ':' + repo_name

# Initialize new repo
def init_repo(full_repo_name):
  proc = sp.run(['restic', 'init', '-r', full_repo_name],
                capture_output=True, text=True)
  if proc.returncode == 0:
    logging.info('Created new repo ' + full_repo_name)
  else:
    logging.error('Problem creating new repo ' + full_repo_name + '--\n' + proc.stderr)

# Kick off a backup
def backup(full_repo_name, backup_path):
  logging.info('Backing up ' + backup_path + ' to repo ' + full_repo_name)
  proc = sp.run(['restic', '-r', full_repo_name, 'backup', backup_path],
                capture_output=True, text=True)
  if proc.returncode == 0:
    logging.info('Successfully backed up ' + backup_path + ' to repo ' + full_repo_name)
    return proc.stdout
  else:
    logging.info('Problem backing up ' + backup_path + ' to repo ' + full_repo_name)
    return proc.stderr

def check_integrity(short_repo_name):
  full_repo_name = get_full_repo_name(b2_bucket, short_repo_name)
  logging.info('Checking integrity of repo ' + full_repo_name)
  proc = sp.run(['restic', '-r', full_repo_name, 'check'],
                capture_output=True, text=True)
  if proc.returncode == 0:
    message = 'Repo integrity looks good for ' + full_repo_name
    logging.info(message)
    return message
  else:
    message = 'Problem with repo integrity for ' + full_repo_name + proc.stderr
    logging.info(message)
    return message

# Create repo if needed, then backup given path
def init_and_backup(short_repo_name, backup_path):
  full_repo_name = get_full_repo_name(b2_bucket, short_repo_name)

  # Check if repo exist, init if not
  proc = sp.run(['restic', '-r', full_repo_name, 'snapshots'],
                capture_output=True, text=True)
  if proc.returncode == 0:
    logging.info('Repo exists: ' + full_repo_name)
  else:
    logging.info('Repo does not exist, creating: ' + full_repo_name)
    init_repo(full_repo_name)

  # Kick off the backup
  return backup(full_repo_name, backup_path)

# Provide stats
def repo_snapshots(short_repo_name):
  full_repo_name = get_full_repo_name(b2_bucket, short_repo_name)
  proc = sp.run(['restic', 'snapshots', '-r', full_repo_name],
                capture_output=True, text=True)
  if proc.returncode == 0:
    return proc.stdout
  else:
    return proc.stderr
