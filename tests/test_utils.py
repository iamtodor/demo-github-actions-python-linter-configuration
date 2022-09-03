from utils import custom_sum


def test_custom_sum():
    expected_sum = 6
    actual_sum = custom_sum(4, 2)
    assert expected_sum == actual_sum