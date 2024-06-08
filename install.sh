#!/bin/sh

# Copy default config file
config_dir='~/.config/redshift-scheduler'
cmd="mkdir -p $config_dir"
echo $cmd
eval $cmd
cmd="cp rules.conf $config_dir/"
echo $cmd
eval $cmd

# Install the app
script="/usr/local/bin/redshift-smooth"
cmd="sudo cp redshift_smooth.py $script"
echo $cmd
eval $cmd
cmd="sudo chmod a+rx $script"
echo $cmd
eval $cmd

# -----------------------------------------------
# Add cron job

cron_job="*/5 * * * * $script"

# Get the current user's crontab
current_crontab=$(crontab -l 2>/dev/null)

# Check if the cron job already exists
if echo "$current_crontab" | grep -Fq "$cron_job"; then
  echo "Cron job already exists."
else
  # Add the new cron job to the current crontab
  (echo "$current_crontab"; echo "$cron_job") | crontab -

  # List cron jobs
  current_crontab=$(crontab -l 2>/dev/null)
  echo "$current_crontab"

  echo "Cron job added."
fi
