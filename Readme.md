
# redshift-smooth

A Python script that can be used as an in-place substitution for [spantaleev/redshift-scheduler](https://github.com/spantaleev/redshift-scheduler).

This program should be used with 'redshift' (make sure it is installed).

This program works similar to 'redshift-scheduler' and supports config-file of the same format. But it is written in Python, so it doesn't need to be compiled and works out-of-the-box on every system that supports Python.

## What is it for

This script allows you to define rules for `redshift` according to system time. You can define some fixed rules to instantly switch the screen temperature and also some *smooth* rules that will gradually increase or decrease the temperature.

## Config examples

Following rules will define that at 9 am the temperature will gradually increase from 6200K to 6500K and stay fixed until 5 pm.

    08:00 -> 09:00 | 6200K
    09:00 -> 09:30 | 6500K
    09:30 -- 17:00 | 6500K

>Actually the last rule here is redundant, the same result will be achieved without the third line.

## Configuration file path

The config-file must be placed to `~/.config/redshift-scheduler/rules.conf.` This is done automatically by running `install.sh`

The default config may be used as an example. You can find it in this repository: `rules.conf`

## Installation

Run the install script:

    ./install.sh

Alternatively you can manually install the script. Copy it to `/usr/bin` directory and add a `cron` task to automatically run this script every 1 minute or at any other frequency if you wish.

As this script modifies display settings you have to attach it to all the displays in the system. Or to a single particular display if you wish. Expample of a cron task for the first display:

    */1 * * * * DISPLAY=:0 redshift-smooth

## Python version

Tested with Python 3.12. Should also work well with other versions.

## License

This software is distributed under the GPL-3.0 license.
