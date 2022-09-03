from utils import custom_multiplication, custom_sum


def test_custom_sum():
    expected_result = 6
    actual_result = custom_sum(4, 2)
    assert expected_result == actual_result


def test_custom_multiplication():
    expected_result = 6
    actual_result = custom_multiplication(3, 2)
    assert expected_result == actual_result
