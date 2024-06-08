#!/bin/python

import re
import pathlib
import os
import datetime
import argparse
import sys
import io



# ===============================================
#   Global variables and settings
# -----------------------------------------------

CONFIG_PATH = "~/.config/redshift-scheduler/rules.conf"

DESCRIPTION = f"""

This program should be used with 'redshift' (make sure it is installed).

This program works similar to 'redshift-scheduler' and supports config-file of the same format. But it is written in Python, so it doesn't need to be compiled and works out-of-the-box on every system that supports Python.

Configuration file path:
{CONFIG_PATH}
"""

ARGS = None




# ===============================================
#   Utility functions
# -----------------------------------------------

def parse_arguments() :
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    parser.add_argument(
        '-v', '--verbose', action='store_true', 
        help='Enable verbose mode')
    parser.add_argument(
        '-s', '--silent', action='store_true', 
        help='Do not show any output messages')
    args = parser.parse_args()
    return args

# Print if verbose mode is on
def print_v( str ) :
    """
    A wrapper around standard print function that checks the state of a global verbose flag and prints the message only if it is set.
    """
    if not ARGS.verbose : return
    print( str )
    return

""" 
# Not needed because argparse has auto help message
def show_help() :
    print( DESCRIPTION )
    
    # Show the list of available arguments
    if ARGS is None:
        return
    parsed_args_dict = vars(ARGS)
    parsed_args_list = list(parsed_args_dict.items())
    print("List of all parsed arguments:")
    for arg, value in parsed_args_list:
        print(f"{arg}: {value}")

    return """

# Custom class to ignore writes
# Used to mute the program output 
# if --silent or -s arguments passed
class dev_null :
    def write(self, _):
        pass
    def flush(self):
        pass

def parse_config_str(s):
    # Prepare string
    s = s.replace('k', 'K')

    # Define regex patterns
    time_pattern = r'(\d{2}:\d{2})'
    arrow_pattern = r'(--|->)'
    number_pattern = r'(\d+K)'

    # Extract data using regex
    times = re.findall(time_pattern, s)
    arrow = re.search(arrow_pattern, s)
    number = re.search(number_pattern, s)

    # Prepare the result
    result = {
        "start": times[0] if times else None,
        "end": times[1] if len(times) > 1 else None,
        "arrow": arrow.group(0) if arrow else None,
        "temp": number.group(0) if number else None
    }
    return result

def read_file_lines( path ):
    lines_array = []
    f = open(path,"r")
    lines_array = f.readlines()
    f.close()
    return lines_array

def str_strip ( string ):
    """Strip all spaces from a string:
    at the begining, at the end and in the middle.
    """
    return " ".join( string.split() )

def trim_comments_single( str ):
    """Trim comments from a string like this:
    Some data # this is a comment
    """
    return str.split('#', 1)[0]

def trim_comments( strings ):
    """
    Trim comments and void lines.
    Accepts: array of strings.
    Returns: array of strings.
    """
    results = []
    for str in strings:
        str = trim_comments_single( str )
        str = str_strip( str )
        if len( str ) == 0 : continue
        if str.startswith("#") : continue
        results.append( str )
    return results

def parse_config( rules_strings ):
    rules = []
    rules_strings = trim_comments( rules_strings )
    for str in rules_strings :
        str = parse_config_str( str )
        rules.append( str )
    return rules

def time_to_minutes( hours, minutes ):
    return hours * 60 + minutes

def time_str_to_minutes( time_str ) :
    """
    This function takes a time string in the format "HH:MM" and returns the total
    number of minutes represented by that time.
    """
    hours, minutes = map(int, time_str.split(':'))
    return time_to_minutes( hours, minutes )

def rules_minutes( rules ):
    """
    Convert time of all rules to minutes (strings to integer values).
    """
    result = []
    for rule in rules:
        rule['start']   = time_str_to_minutes( rule['start'] )
        rule['end']     = time_str_to_minutes( rule['end'] )
        result.append( rule )
    return result

def find_rule_index( rules, current_time ):
    """
    Find the index of a rule that will fit to the current time.
    Returns the integer index of a rule in the `rules` array
    """
    for i in range( 0, len(rules)-1 ):
        rule = rules[i]
        if rule['start'] > current_time :
            return i-1
        if rule['end'] >= current_time :
            return i
    return -1

def set_temp( temp ):
    """
    Execute a command to set the calculated temperature.

    According to `redshift` rules the temperature
    must be between 1000K and 25000K.
    """
    v_message = """
        redshift doesn't allow to set values 
        out of the range of 1000K - 25000K
        """
    print( "Temperature to set: {}".format( temp ) )
    temp_value = get_temp_value( temp )
    if temp_value < 1000 :
        temp = "1000K"
        print( "The temperature must not be lower then 1000K" )
        print_v( v_message )
    if temp_value > 25000 :
        temp = "25000K"
        print( "The temperature must not be higher then 25000K" )
        print_v( """
        redshift doesn't allow to set values 
        out of the range of 1000K - 25000K
        """)
    
    cmd = "redshift -P -O {}".format( temp )
    if ARGS.silent :
        cmd += ' > /dev/null'
    print_v( "Shell command to execute: \n{}".format( cmd ) )
    os.system( 
        cmd
        )
    return

def get_temp_value( temp_str ):
    """
    This function extracts the temperature value from a string formatted like "6400K"
    and returns it as an integer.

    Returns extracted temperature value as an integer.
    """
    if temp_str == '' : return 0
    temp_str = temp_str.rstrip('K')
    if temp_str == '' : return 0
    return int(temp_str)

def calculate_temp( rule, time, prev_temp ):
    """
    Calculate temperature according to the rule and the ammount of time passed from the start shift.

    Returns the temperature string formatted like "6400K".
    """
    if time < rule['start'] :   return prev_temp
    if time > rule['end'] :     return rule['temp']
    if rule['arrow'] == '--':   return rule['temp']

    # Calculate percentage of passed time
    max_d_time = rule['end'] - rule['start']
    if max_d_time == 0 : return rule['temp']
    d_time = time - rule['start']
    proportion = d_time / max_d_time
    
    # Apply the same proportion to temperature shift
    max_temp = get_temp_value( rule['temp'] )
    min_temp = get_temp_value( prev_temp )
    max_d_temp = max_temp - min_temp
    d_temp = max_d_temp * proportion
    d_temp = int( d_temp )
    result = min_temp + d_temp
    return "{}K".format( result )


# ===============================================
#   Start 
# -----------------------------------------------

def main():
    global ARGS

    # process args
    ARGS = parse_arguments()
    if ARGS.silent :
        sys.stdout = dev_null()

    # get correct full config file path
    config_path = pathlib.PosixPath( CONFIG_PATH )
    config_path = config_path.expanduser()

    # Check if config file exists
    if ( not os.path.exists( config_path ) ) :
        print( "Config file not found at path:" )
        print( config_path )
        exit( os.EX_CONFIG )
    else:
        print_v( "Config file found at:" )
        print_v( config_path )

    # Read config file
    rules_str = read_file_lines( config_path )

    # Parse redshift rules from config file
    rules = parse_config( rules_str )

    # Terminate if no rules in the config
    if len( rules ) == 0 :
        print("No rules in the config file. Nothing to do.")
        exit( os.EX_OK )

    # Convert rules time to minutes
    rules = rules_minutes( rules )

    # Sort rules
    rules = sorted( rules, key = lambda d: d['start'])

    # Get current time in munutes
    now = datetime.datetime.now()
    current_time = time_to_minutes( now.hour, now.minute )
    print_v( "Current time in minutes: {}".format( current_time ) )   

    # Choose an applicable rule
    i = find_rule_index( rules, current_time )
    print_v( "Rule to be used: \n{}".format( rules[i] ) )
    print_v( "Previous rule temperature: {}".format( rules[ i-1 ]['temp'] ) )

    # Calculate and set new temp
    temp = calculate_temp(
        rules[i], 
        current_time, 
        rules[ i-1 ]['temp'] )
    set_temp( temp )

    return # main()


if __name__ == '__main__':
    main()