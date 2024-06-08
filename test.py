#!/bin/python

import redshift_smooth as rs


# ===============================================
#   Global variables and settings
# -----------------------------------------------

# Final result
NoFails = True



# ===============================================
#   Utility and output functions
# -----------------------------------------------

def passed ( testName ):
    print( '\033[92m' + 'OK' + '\033[0m' + ' - ' + testName )
    return

def failed ( testName ):
    global NoFails
    NoFails = False
    print( '\033[91m' + 'Fail - ' + testName + '\033[0m' )
    return
    
def assert_equal( testName, data, answer ):
    result = ( data == answer )
    printFunction = passed if result else failed
    printFunction( testName )
    return result



# ===============================================
#   Tests
# -----------------------------------------------

assert_equal( "parse_config_str : No spaces",
    rs.parse_config_str( "09:30--17:00|6500K" ),
    {
        "start": "09:30",
        "end": "17:00",
        "arrow" : '--',
        "temp" : "6500K",
    }
)

assert_equal( "parse_config_str : With spaces",
    rs.parse_config_str( "   10:42  ->  07:00    | 1234K " ),
    {
        "start": "10:42",
        "end": "07:00",
        "arrow" : '->',
        "temp" : "1234K",
    }
)

assert_equal( "parse_config_str : With tabs",
    rs.parse_config_str( " \t 09:30 -- 17:00 \t| 6500K" ),
    {
        "start": "09:30",
        "end": "17:00",
        "arrow" : '--',
        "temp" : "6500K",
    }
)

assert_equal( "parse_config_str : lower-case K",
    rs.parse_config_str( "09:30 -- 17:00 | 6500k" ),
    {
        "start": "09:30",
        "end": "17:00",
        "arrow" : '--',
        "temp" : "6500K",
    }
)

assert_equal( "trim_comments_single : Trim comment",
    rs.trim_comments_single( "A sting with # a comment" ),
    "A sting with "
)


time = "09:30"
assert_equal( "time_str_to_minutes : " + time,
    rs.time_str_to_minutes( time ),
    9*60 + 30
)

time = '1:1'
assert_equal( "time_str_to_minutes : " + time,
    rs.time_str_to_minutes( time ),
    1*60 + 1
)

time = '00:00'
assert_equal( "time_str_to_minutes : " + time,
    rs.time_str_to_minutes( time ),
    0
)

assert_equal( "rules_minutes",
    rs.rules_minutes( [ {
        "start": "01:35",
        "arrow" : '--',
        "temp" : "6500K",
        "end": "2:22",
    } ] ),
    [ {
        "start": 1*60 + 35,
        "end": 2*60 + 22,
        "arrow" : '--',
        "temp" : "6500K",
    } ]
)

rules = [
    {'start': 540,  'end': 570,     'arrow': '->', 'temp': '4500K'}, 
    {'start': 570,  'end': 1020,    'arrow': '--', 'temp': '6500K'}, 
    {'start': 1020, 'end': 1170,    'arrow': '->', 'temp': '3500K'} ]
assert_equal( "find_rule_index: inside a rule",
    rules[ rs.find_rule_index( rules, 900 ) ],
    {'start': 570,  'end': 1020,    'arrow': '--', 'temp': '6500K'}
)

rules = [
    {'start': 480,  'end': 540,     'arrow': '->', 'temp': '6200K'}, 
    {'start': 600,  'end': 630,     'arrow': '->', 'temp': '6500K'}, 
    {'start': 1020, 'end': 1170,    'arrow': '->', 'temp': '3500K'}, 
    {'start': 1260, 'end': 1380,    'arrow': '->', 'temp': '2400K'}]
assert_equal( "find_rule_index: between rules",
    rules[ rs.find_rule_index( rules, 900 ) ],
    {'start': 600,  'end': 630,     'arrow': '->', 'temp': '6500K'}
)

config_str = [
    {'start': 480, 'end': 540,      'arrow': '->', 'temp': '6200K'}, 
    {'start': 600, 'end': 630,      'arrow': '->', 'temp': '6500K'}, 
    {'start': 1020, 'end': 1170,    'arrow': '->', 'temp': '3500K'}, 
    {'start': 1260, 'end': 1380,    'arrow': '->', 'temp': '2400K'} ]
assert_equal( "find_rule_index: before first rule",
    rules[ rs.find_rule_index( rules, 420 ) ],
    {'start': 1260, 'end': 1380, 'arrow': '->', 'temp': '2400K'}
)

config_str = [
    {'start': 480, 'end': 540,      'arrow': '->', 'temp': '6200K'},
    {'start': 540, 'end': 570,      'arrow': '->', 'temp': '6500K'},
    {'start': 1020, 'end': 1170,    'arrow': '->', 'temp': '3500K'},
    {'start': 1260, 'end': 1380,    'arrow': '->', 'temp': '2400K'} ]
assert_equal( "find_rule_index: after the last",
    rules[ rs.find_rule_index( rules, 1410 ) ],
    {'start': 1260, 'end': 1380, 'arrow': '->', 'temp': '2400K'}
)

temp = "6400K"
assert_equal( "get_temp_value : " + temp,
    rs.get_temp_value( temp ),
    6400
)

temp = "K"
assert_equal( "get_temp_value : " + temp,
    rs.get_temp_value( temp ),
    0
)

assert_equal( "get_temp_value : empty string",
    rs.get_temp_value( "" ),
    0
)

rule = { "start": 0, "end": 100, "arrow" : '->', 
    "temp" : "1000K" }
time = 50
prev_temp = "900K"
expected = "950K"
assert_equal(
    "calculate_temp - go up : {} -> {}, {} = {}"
    .format(prev_temp, rule['temp'], time, expected),
    rs.calculate_temp( rule, time, prev_temp ),
    expected)
    

rule = { "start": 0, "end": 100, "arrow" : '->', 
    "temp" : "1000K" }
time = 50
prev_temp = "1100K"
expected = "1050K"
result = rs.calculate_temp( rule, time, prev_temp )
assert_equal(
    "calculate_temp - go down : {} -> {}, {} = {}"
    .format(prev_temp, rule['temp'], time, expected),
    result,
    expected)

prev_temp = "6500K"
rule = {'start': 1020, 'end': 1140,    'arrow': '->', 'temp': '5500K'}
time = 1080
expected = "6000K"
result = rs.calculate_temp( rule, time, prev_temp )
eq = assert_equal(
    "calculate_temp : {} -> {}, {} = {}"
    .format(prev_temp, rule['temp'], time, expected),
    result,
    expected)
if ( not eq ) : print( "Actual result: " + result )




# ===============================================
#   Final results report
# -----------------------------------------------

print("\nTesting results:")
if ( NoFails ) :
    passed( "All test passed successfully" )
else :
    failed( "Some test failed" )
print("")

