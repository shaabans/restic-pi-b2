#!/usr/bin/python3
import config
import restic
import gmail

def main():
  if not restic.is_running():
    email_output = ''
    for backup_set in config.backup_sets:
      email_output = (email_output
                      + '\nResult of backing up ' + backup_set[1]
                      + ' to repo ' + backup_set[0]
                      + ':\n'
                      + restic.init_and_backup(backup_set[0], backup_set[1])
                      + restic.repo_snapshots(backup_set[0]))
    print(email_output)

    if config.send_gmail:
      gmail.send_email(email_output)

  else:
    print('Another Restic process is running, aborting.')

if __name__ == '__main__':
  main()
