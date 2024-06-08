
# redshift-smooth

A Python script that can be used as an in-place substitution for [spantaleev/redshift-scheduler](https://github.com/spantaleev/redshift-scheduler).

This program should be used with 'redshift' (make sure it is installed).

This program works similar to 'redshift-scheduler' and supports config-file of the same format. But it is written in Python, so it doesn't need to be compiled and works out-of-the-box on every system that supports Python.

## What is it for

This script allow you to define rules for `redshift` according to system time. You can define some fixed rules the binary switch the screen temperature and also some *smooth* rules that will gradually increase of decreate the temperature.

## Config examples

The following rules will define that at 9 am the temperature will gradually increese from 6200K to 6500K and stay fixed until 5 pm.

    08:00 -> 09:00 | 6200K
    09:00 -> 09:30 | 6500K
    09:30 -- 17:00 | 6500K

>Actually the last rule here is supplementary, the same result will be achieved withour the third line.

## Configuration file path

The config-file must be placed to `~/config/redshift-scheduler/rules.conf.` This is done automatically by running `install.sh`

The default config may be used as an example. You can find it in this repository: `rules.conf`

## Installation

Run the install script:

    ./install.sh

Alternatively you can manually install the script. Copy it to `/usr/local/bin` directory and add a `cron` task to automatically run this script every 5 minutes (or at any other frequency if you wish).

## Licence

This software is distributed under the GPL licence.