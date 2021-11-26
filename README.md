# Restic / Raspberry Pi / BackBlaze B2 Backup Starter Kit
This project is a bare-bones example of a nightly offsite backup from a network attached storage (NAS) device built with a [Raspberry Pi](https://www.raspberrypi.org/). It includes an example setup and a backup script for using a Pi-based NAS device that will automatically back itself up to [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html) using the excellent [Restic](https://github.com/restic/restic).

In a nutshell the idea is:
1. Backup all the computers in your house to one place, the Raspberry Pi-based NAS running quietly in your kitchen.
2. Automatically back the NAS up to offsite storage in the wee hours.

## Quick Start

### Prerequisites
- Put your Raspberry Pi on a fast connection on your home network. A [static IP address](https://pimylifeup.com/raspberry-pi-static-ip-address/) and a wired connection will make life better.
- Setup a [Raspberry Pi as a NAS](https://pimylifeup.com/raspberry-pi-nas/). If you're drinking Mac/Apple Kool-Aid go with the option of using AFP (Apple Filing Protocol) with [Netatalk](http://netatalk.sourceforge.net/).
- Make sure Python 3.x is installed on your Pi (you should be able to run `python3 --version` and get a non-error).
- Install [psutil](https://github.com/giampaolo/psutil/blob/master/INSTALL.rst) on the Pi.
- Setup an account on [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html), setup a bucket to backup to, and get the bucket's API ID and key (Restic supports a bunch of [other destinations](https://restic.readthedocs.io/en/latest/030_preparing_a_new_repo.html) other than B2, just tweak the scripts if you want to use something else).
- Mount the NAS on your computer(s) and put the things you want to backup nightly there. An example of how I do this is in the [My Setup](#my-setup) section.

### Running the Backup Script
Once you're ready to backup the Pi NAS:

1. Copy this repo somewhere on the Pi where you'll run it.
1. Copy `config-template.py` to `config.py`.
1. Edit `config.py` to reflect your setup and preferences, the comments should spell everything out.
1. Run `backup.py` as often as you'd like to backup. I like putting this kind of cron job into `/etc/cron.d` as a file named `restic-backups` that looks something like this:

```
# Run a Restic/B2 backup every morning at at 1:13am
13 1 * * * root cd /home/nas/restic-pi-b2 && python3 backup.py
```

## Motivation
Nowadays most of our computers sync important data to offsite/cloud storage. Think [iCloud](icloud.com) if you're on a Mac, or [Box](box.com), or [Dropbox](dropbox.com), or whatever you're using. This is good, but you probably want more than just a sync for your most important data:

1. [Sync is not backup](https://www.backblaze.com/blog/cloud-backup-vs-cloud-sync/). Syncing is a good thing, but if you accidentally delete your precious pictures of your beloved late cat Fluffy in one place, Fluffy gets deleted everywhere. A good backup, on the other hand, maintains versions of your old data, keeping any silly mistakes from turning into you losing your important stuff.
1. [3-2-1](https://www.nakivo.com/blog/3-2-1-backup-rule-efficient-data-protection-strategy/) is a good start. The 3-2-1 backup rule of thumb suggests keeping 3 copies of your important data, using at least 2 different forms of storage media, and keeping at least 1 copy offsite.

## <a id="my-setup"></a>My Setup
My house has 3 Mac users, 2 of which don't really want to be bothered with details like backups. Each user's computer is setup to send a [Time Machine](https://support.apple.com/en-us/HT201250) backup to their special place on the NAS, which gets backed up nightly.

So in our case it makes sense to use Apple's [AFP](https://en.wikipedia.org/wiki/Apple_Filing_Protocol) on the Pi (like [this](https://pimylifeup.com/raspberry-pi-afp/)). The Pi's `/etc/netatalk/afp.conf` file looks something like this:

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

Each user has their special place on the NAS, and even though they're all on the same disk we limit the space each can have so no single Time Machine backup eats up the entire disk. Which they will - Time Machine backups grow until there's no more disk space, with no option to limit this that I'm aware of.

The whole /media/nastimemachine volume gets incrementally backed up each night. The first time this runs, it is *very* slow, but pretty soon nightly runs are quick.

## Gotchas

### Time Machine Backups Get Huge
In the example above, disk space is limited to a pre-defined max based on the setup, but it's still useful to trim Time Machine backups themselves using the nice [tmutil](https://ss64.com/osx/tmutil.html) utility that Mac provides. For example, a quick way to blast every single huge Time Machine backup except the latest one on your Mac (use caution):

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

Alternatives like the [personal backup](https://www.backblaze.com/backup-pricing.html) offered by the same company cost only $60/year per user. It doesn't work for backing up a NAS and doesn't provide as many server-nerd degrees of freedom as I want, but if it works for you it can be far less expensive for the same amount of data. In my case, it was easier to setup Time Machine for each user in the house, since it's just baked into MacOS.

### Backups Fail Due to Lock
Sometimes you'll see a message like this:

`Fatal: unable to create lock in backend: repository is already locked exclusively by PID 6884 on polkadotninja by root (UID 0, GID 0)`

That means that somehow a backup was interrupted, and you'll have to manually remove that lock. You can do that like this:

`restic -r b2:yourb2account:yourb2bucket unlock`

### You Want To Do Something Slow
Let's say you want to reindex a Restic repository, but it takes forever and you don't want to stay logged into your Pi for a day while it works.  Use the screen command to disconnect from a session while it works. Log into your Pi, then start a new screen session and run the command:

```
screen
restic -r b2:yourb2account:yourb2bucket rebuild-index
```

To disconnect from that session, just hit `control-a` followed by `d` - now you can safely log out of the Pi without interrupting the command. When you want reconnect to the session to see if it works, just log back into the Pi and type `screen -r`

## To Do List
- Better logging
- More email options to report on nightly backups (now the only option is to use a Gmail account's SMTP server)
- Prune Restic repos on offsite storage to contain space based on a policy you can configure
- Consider incremental data file integrity check with `--read-data-subset=n/t` option in Restic

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
