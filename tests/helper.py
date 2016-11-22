import csv

def write_to_separated_value_file(field_names, delimiter, items, output_file_path):
    with open(output_file_path, 'w', 1) as output_file:
        writer = csv.DictWriter(output_file, fieldnames = field_names, delimiter = delimiter)
        writer.writeheader()
        for item in items:
            writer.writerow(item)

def assert_equal_field_values(unit_test, item1, item2, field_names):
    for field_name in field_names:
        unit_test.assertEqual(item1[field_name], item2[field_name])

next_user_id = 1
def create_test_user(groups):
    global next_user_id
    firstName = 'User_%d' % next_user_id
    next_user_id += 1    
    user = {
        'firstname': firstName,
        'lastname': 'Test',
        'email': '%s_email@example.com' % firstName,
        'country': 'CA' if (next_user_id % 2 == 0) else 'US',
        'groups': groups
    }
    return user


def assert_equal_users(unit_test, expected_users, actual_users):
    actual_users_by_email = dict((user['email'], user) for user in actual_users)
    unit_test.assertEqual(len(expected_users), len(actual_users_by_email))

    for expected_user in expected_users:
        actual_user = actual_users_by_email.get(expected_user['email'])
        unit_test.assertIsNotNone(expected_user)            
        assert_equal_field_values(unit_test, expected_user, actual_user, ['firstname', 'lastname', 'email', 'country'])
        unit_test.assertSetEqual(set(expected_user['groups']), set(actual_user['groups']))


    
