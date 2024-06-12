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
    { "start": "09:30", "end": "17:00", "arrow" : '--', "temp" : "6500K" }
)

assert_equal( "parse_config_str : lower-case K",
    rs.parse_config_str( "09:30 -- 17:00 | 6500k" ),
    { "start": "09:30", "end": "17:00", "arrow" : '--', "temp" : "6500K" }
)

assert_equal( "trim_comments_single : Trim comment",
    rs.trim_comments_single( "A sting with # a comment" ),
    "A sting with "
)


def test_time_str_to_minutes_general():
    time = "09:30"
    assert_equal( "time_str_to_minutes : " + time,
        rs.time_str_to_minutes( time ),
        9*60 + 30
    )
test_time_str_to_minutes_general()

def test_time_str_to_minutes_no_leading_zero():
    time = '1:1'
    assert_equal( "time_str_to_minutes : " + time,
        rs.time_str_to_minutes( time ),
        1*60 + 1
    )
test_time_str_to_minutes_no_leading_zero()

def test_time_str_to_minutes_zero():
    time = '00:00'
    assert_equal( "time_str_to_minutes : " + time,
        rs.time_str_to_minutes( time ),
        0
    )
test_time_str_to_minutes_zero()

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

def test_find_rule_inside() :
    rules = [
        {'start': 540,  'end': 570,     'arrow': '->', 'temp': '4500K'}, 
        {'start': 570,  'end': 1020,    'arrow': '--', 'temp': '6500K'}, 
        {'start': 1020, 'end': 1170,    'arrow': '->', 'temp': '3500K'} ]
    time = 900
    rule = rs.find_rule( rules, time )
    result = assert_equal( "find_rule: inside a rule",
        rule,
        {'start': 570,  'end': 1020,    'arrow': '--', 
        'temp': '6500K', 'prev_temp': '4500K'}
    )
    if not result :
        print( "{}\n".format( rule ) )
test_find_rule_inside()

def test_find_rule_between() :
    rules = [
        {'start': 480,  'end': 540,     'arrow': '->', 'temp': '6200K'}, 
        {'start': 600,  'end': 630,     'arrow': '->', 'temp': '6500K'}, 
        {'start': 1020, 'end': 1170,    'arrow': '->', 'temp': '3500K'}, 
        {'start': 1260, 'end': 1380,    'arrow': '->', 'temp': '2400K'}]
    time = 900
    rule = rs.find_rule( rules, time )
    result = assert_equal( "find_rule: between rules",
        rule,
        {'start': 600,  'end': 630,     'arrow': '->', 
        'temp': '6500K', 'prev_temp': '6200K'}
    )
    if not result :
        print( "{}\n".format( rule ) )
test_find_rule_between()

def test_find_rule_before_first():
    rules = [
        {'start': 480, 'end': 540,      'arrow': '->', 'temp': '6200K'}, 
        {'start': 600, 'end': 630,      'arrow': '->', 'temp': '6500K'}, 
        {'start': 1020, 'end': 1170,    'arrow': '->', 'temp': '3500K'}, 
        {'start': 1260, 'end': 1380,    'arrow': '->', 'temp': '2400K'} ]
    time = 420
    rule = rs.find_rule( rules, time )
    result = assert_equal( "find_rule: before first rule",
        rule,
        {   'start': 1260, 'end': 1380, 'arrow': '->', 
            'temp': '2400K', 'prev_temp': '3500K'}
    )
    if not result :
        print( "{}\n".format( rule ) )
test_find_rule_before_first()

def test_find_rule_after_last():
    rules = [
        {'start': 480, 'end': 540,      'arrow': '->', 'temp': '6200K'},
        {'start': 540, 'end': 570,      'arrow': '->', 'temp': '6500K'},
        {'start': 1020, 'end': 1170,    'arrow': '->', 'temp': '3500K'},
        {'start': 1260, 'end': 1380,    'arrow': '->', 'temp': '2400K'} ]
    time = 1410
    rule = rs.find_rule( rules, time )
    result = assert_equal( "find_rule: after the last",
        rule,
        {'start': 1260, 'end': 1380, 'arrow': '->', 
            'temp': '2400K', 'prev_temp': '3500K'}
    )
    if not result :
        print( "{}\n".format( rule ) )
test_find_rule_after_last()

def test_find_rule_next_day():
    rules = [
        {'start': 1020, 'end': 1170,    'arrow': '->', 'temp': '3500K'},
        {'start': 1260, 'end': 1380,    'arrow': '->', 'temp': '2400K'},
        {'start': 1380, 'end': 60,      'arrow': '->', 'temp': '2100K'},
        {'start': 60,   'end': 480,     'arrow': '--', 'temp': '2200K'},
        ]
    time = 5
    rule = rs.find_rule( rules, time )
    result = assert_equal( "find_rule: next day",
        rule,
        {'start': 1380, 'end': 60, 'arrow': '->', 
        'temp': '2100K', 'prev_temp': '2400K'}
    )
    if not result :
        print( "{}\n".format( rule ) )
test_find_rule_next_day()

def test_get_temp_value_general():
    temp = "6400K"
    assert_equal( "get_temp_value : " + temp,
        rs.get_temp_value( temp ),
        6400
    )
test_get_temp_value_general()

def test_get_temp_value_k():
    temp = "K"
    assert_equal( "get_temp_value : " + temp,
        rs.get_temp_value( temp ),
        0
    )
test_get_temp_value_k()

assert_equal( "get_temp_value : empty string",
    rs.get_temp_value( "" ),
    0
)

def test_calculate_temp_up():
    rule = { "start": 0, "end": 100, "arrow" : '->', 
        "temp" : "1000K", "prev_temp" : "900K" }
    time = 50
    expected = "950K"
    assert_equal(
        "calculate_temp - go up : {} -> {}, {} = {}"
        .format(rule['prev_temp'], rule['temp'], time, expected),
        rs.calculate_temp( rule, time ),
        expected)
test_calculate_temp_up()

def test_calculate_temp_down():
    rule = { "start": 0, "end": 100, "arrow" : '->', 
        "temp" : "1000K", "prev_temp" : "1100K" }
    time = 50
    expected = "1050K"
    result = rs.calculate_temp( rule, time )
    assert_equal(
        "calculate_temp - go down : {} -> {}, {} = {}"
        .format(rule['prev_temp'], rule['temp'], time, expected),
        result,
        expected)
test_calculate_temp_down()

def test_calculate_temp_general():
    rule = {'start': 1020, 'end': 1140,    'arrow': '->', 
        'temp': '5500K', "prev_temp" : "6500K"}
    time = 1080
    expected = "6000K"
    result = rs.calculate_temp( rule, time )
    eq = assert_equal(
        "calculate_temp : {} -> {}, {} = {}"
        .format(rule['prev_temp'], rule['temp'], time, expected),
        result,
        expected)
    if ( not eq ) : print( "Actual result: " + result )
test_calculate_temp_general()

def test_calculate_temp_next_day():
    rule = {'start': 1380, 'end': 60,    'arrow': '->', 
        'temp': '5500K', "prev_temp" : "6500K"}
    time = 0
    expected = "6000K"
    result = rs.calculate_temp( rule, time )
    eq = assert_equal(
        "calculate_temp - next day : {} -> {}, {} = {}"
        .format(rule['prev_temp'], rule['temp'], time, expected),
        result,
        expected)
    if ( not eq ) : print( "Actual result: " + result )
test_calculate_temp_next_day()

def test_calculate_temp_before_rule():
    rule = {'start': 60, 'end': 120,    'arrow': '->', 
        'temp': '5500K', "prev_temp" : "6500K"}
    time = 0
    expected = "6500K"
    result = rs.calculate_temp( rule, time )
    eq = assert_equal(
        "calculate_temp - before_rule : {} -> {}, {} = {}"
        .format(rule['prev_temp'], rule['temp'], time, expected),
        result,
        expected)
    if ( not eq ) : print( "Actual result: " + result )
test_calculate_temp_before_rule()




# ===============================================
#   Final results report
# -----------------------------------------------

print("\nTesting results:")
if ( NoFails ) :
    passed( "All test passed successfully" )
else :
    failed( "Some test failed" )
print("")

