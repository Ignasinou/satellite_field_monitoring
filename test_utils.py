import csv
from utils import read_field_locations


def test_read_field_locations(tmp_path):
    # Create a temporary CSV file with test data
    csv_data = [
        ['Fileds', 'Locations'],
        ['Field 1', 'Location 1'],
        ['Field 2', 'Location 2'],
        ['Field 3', 'Location 3'],
    ]
    csv_file = tmp_path / 'test.csv'
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)
    result = read_field_locations(csv_file)

    # We ignore the header
    assert len(result) == 3
    assert result[0] == ['Field 1', 'Location 1']
    assert result[1] == ['Field 2', 'Location 2']
    assert result[2] == ['Field 3', 'Location 3']
