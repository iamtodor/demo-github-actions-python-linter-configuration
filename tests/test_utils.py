from utils import custom_sum


def test_custom_sum():
    expected_sum = 6
    actual_sum = custom_sum(4, 2)
    assert expected_sum == actual_sum


def test_custom_multiplication():
    expected_result = 6
    actual_sum = custom_sum(3, 2)
    assert expected_result == actual_sum
