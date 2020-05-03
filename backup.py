#!/usr/bin/python3
import config
import restic_util
import email_util

def main():
  if not restic_util.is_running():
    email_output = ''
    for backup_set in config.backup_sets:
      email_output = (email_output
                      + '\nResult of backing up ' + backup_set[1]
                      + ' to repo ' + backup_set[0]
                      + ':\n'
                      + restic_util.init_and_backup(backup_set[0], backup_set[1])
                      + restic_util.repo_snapshots(backup_set[0])
                      + restic_util.check_integrity(backup_set[0]))
    print(email_output)

    if config.send_gmail:
      email_util.send_email(email_output)

  else:
    print('Another Restic process is running, aborting.')

if __name__ == '__main__':
  main()
