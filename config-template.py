# Copy this file to 'config.py' and replace with your real values below:

# The name of the B2 bucket you've created, which will be used for all backups.
b2_bucket = 'my-b2-bucket-name'

# The ID and key for the B2 app key you want to use. You can either use
# the master application key, or a regular application key.
b2_account_id = 'myb2accountid'
b2_account_key = 'myb2accountkey'

# The password you'll use for all of your repos. If you lose this, all your
# backup data will be useless, so hang onto it.
restic_password = 'mypasswordthatiwillneverlose'

# Each array within the main array represents a Restic repository name and
# a file path to backup there in the form of: [repo_name, path_to_backup]
backup_sets = [
  ['restic_repo_name1', '/my/path/to/backup1'],
  ['restic_repo_name2', '/my/path/to/backup2']
]
