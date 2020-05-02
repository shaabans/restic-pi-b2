#!/usr/bin/python3
import config
import restic

def main():
  if not restic.is_running():
    for backup_set in config.backup_sets:
      restic.init_and_backup(backup_set[0], backup_set[1])
  else:
    print('Another Restic process is running, aborting.')

if __name__ == '__main__':
  main()
