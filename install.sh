#!/bin/sh

# Copy default config file
config_dir="$HOME/.config/redshift-scheduler"
cmd="mkdir -p $config_dir"
echo $cmd
eval $cmd
cmd="cp rules.conf $config_dir/"
echo $cmd
eval $cmd

# Install the app
script="/usr/bin/redshift-smooth"
cmd="sudo cp redshift_smooth.py $script"
echo $cmd
eval $cmd
cmd="sudo chmod a+rx $script"
echo $cmd
eval $cmd

# -----------------------------------------------
# Add cron job for all displays

# Function to add cron job for a specific display
add_cron_job() {
  local display=$1
  local cron_job="*/5 * * * * DISPLAY=$display XAUTHORITY=$HOME/.Xauthority $script"
  
  # Get the current user's crontab
  current_crontab=$(crontab -l 2>/dev/null)

  # Check if the cron job already exists
  if echo "$current_crontab" | grep -Fq "$cron_job"; then
    echo "Cron job for display $display already exists."
  else
    # Add the new cron job to the current crontab
    (echo "$current_crontab"; echo "$cron_job") | crontab -

    # List cron jobs
    current_crontab=$(crontab -l 2>/dev/null)
    echo "$current_crontab"

    echo "Cron job for display $display added."
  fi
}

# Get the list of active displays
displays=$(who | grep '(:' | awk '{print $5}' | tr -d '()' | sort | uniq)

# Add cron job for each display
for display in $displays; do
  add_cron_job $display
done

# Fallback if no active displays are found
if [ -z "$displays" ]; then
  add_cron_job ":0"
fi
