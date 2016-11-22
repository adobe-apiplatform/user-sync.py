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
    