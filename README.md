# Restic / Raspberry Pi / BackBlaze B2 Backup Starter Kit
This project provides a brief tutorial, example setup, and backup script for using a [Raspberry Pi](https://www.raspberrypi.org/) as a network attached storage (NAS) device that will automatically back itself up to [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html) using the excellent [Restic](https://github.com/restic/restic).

## Quick Start

### Prerequisites
- Setup your Raspberry Pi on your home network. I recommend setting up a [static IP address](https://pimylifeup.com/raspberry-pi-static-ip-address/) to make life easier.
- Setup a [Raspberry Pi as a NAS](https://pimylifeup.com/raspberry-pi-nas/). If you're using a Mac, I recommend the option of using AFP (Apple Filing Protocol) with [Netatalk](http://netatalk.sourceforge.net/).
- Make sure Python 3.x is installed on your Pi (you should be able to run `python3 --version` and get a non-error).
- Install [psutil](https://github.com/giampaolo/psutil/blob/master/INSTALL.rst).
- Setup an account on [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html), setup a bucket to backup to, and get the bucket's API ID and key.
- Mount the NAS on your computer(s) and put things you want to backup there.

### Running the Backup Script
1. Copy this repo somewhere on the Pi where you'll run it.
1. Copy `config-template.py` to `config.py`.
1. Edit `config.py` to reflect your setup and preferences, the comments should spell everything out.
1. Run `back.py` as often as you'd like to backup. I like putting this kind of cron job into `/etc/cron.d` as a file named `restic-backups` that looks something like this:

```
# Run a Restic/B2 backup every morning at at 1:13am
13 1 * * * root cd /home/nas/restic-pi-b2 && python3 back.py
```

## Motivation
Most of our computers sync important data to offsite/cloud storage. Think [iCloud](icloud.com) if you're on a Mac, or [Box](box.com), or [Dropbox](dropbox.com), or whatever you're using. This is good, but you probably want more for your most important data because:

1. [Sync is not backup](https://www.backblaze.com/blog/cloud-backup-vs-cloud-sync/). Syncing is a good thing, but if you delete your precious data accidentally in one place, it gets deleted everywhere. A good backup, on the other hand, maintains versions of your old data, keeping any silly mistakes from turning into you losing your precious work or photos.
1. [3-2-1](https://www.nakivo.com/blog/3-2-1-backup-rule-efficient-data-protection-strategy/) is a good start. The 3-2-1 backup rule of thumb suggests keeping 3 copies of your important data, using at least 2 different forms of storage media, and keeping at least 1 copy offsite.

So in additional to a sync, I like to send the data I care about somewhere offsite.

## My Setup
My house has 3 Mac users, 2 of which don't really want to be bothered with details like backups. Each user's computer is setup to send a [Time Machine](https://support.apple.com/en-us/HT201250) backup to their special place on the NAS, which gets backed up nightly.

The Pi's `/etc/netatalk/afp.conf` file looks something like this:

```
[Global]
  save password = yes

[NASTimeMachineUser1]
  path = /media/nastimemachine/user1
  time machine = yes
  vol size limit = 1500000
  valid users = user1

[NASTimeMachineUser2]
  path = /media/nastimemachine/user2
  time machine = yes
  vol size limit = 1500000
  valid users = user2

[NASTimeMachineUser3]
  path = /media/nastimemachine/user3
  time machine = yes
  vol size limit = 1500000
  valid users = user3
```

Each user has their special place on the NAS, and even though they're all on the same disk we limit the space each can have so no single Time Machine backup eats up the entire disk.

The whole /media/nastimemachine volume gets incrementally backed up each night. The first time this runs, it is *very* slow, but pretty soon nightly runs are quick.

## Gotchas

### Time Machine Backups Get Huge
In the example above, disk space is limited, but it's still sometimes useful to trim Time Machine backups themselves using the nice [tmutil](https://ss64.com/osx/tmutil.html) utility that Mac provides. For example, a quick way to blast every single huge Time Machine backup except the latest one on your Mac (use caution):

```
#!/bin/bash
latest=$(sudo tmutil latestbackup)
sudo tmutil listbackups | while read backup; do
    if [[ "$backup" != "$latest" ]]; then
        sudo tmutil delete "$backup"
    fi
done
```

### B2 Quickly Gets Expensive
B2 is pretty cheap compared to other services, but it can still cost a pretty penny if you let the repo sizes go wild.

In the example above, I allocated 1.5TB for each of 3 NAS users. Using [B2's pricing calculator](https://www.backblaze.com/b2/cloud-storage-pricing.html) this comes out to just south of $300/year.

Alternatives like the [personal backup](https://www.backblaze.com/backup-pricing.html) offered by the same company cost only $60/year per user. It doesn't work for backing up a NAS and doesn't provide as many server-nerd degrees of freedom as I want, but if it works for you it can be far less expensive for the same amount of data.

## To Do List
- Logging backup results
- Email option to report on nightly backups
- Pruning Restic repos on B2 to contain space

## Built With
- [Restic](https://github.com/restic/restic)
- [Raspberry Pi](https://www.raspberrypi.org/)
- [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html)

## Versioning
We use [CalVer](https://calver.org/) with a YY.0M.MICRO format.

## Authors
* **Sam** - *Initial work* - [shaabans](https://github.com/shaabans)

## License
This project is licensed under the [Unlicense](https://unlicense.org) - see the [LICENSE](LICENSE) file for details.
