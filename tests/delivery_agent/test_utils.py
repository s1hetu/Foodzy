from delivery_agent.utils import get_rating_degrees


class TestGetRatingsDegrees:

    def test_get_rating_degrees_scenario1(self):
        rating = 0
        rating, first_half_rating_degrees, second_half_rating_degrees = get_rating_degrees(rating)
        assert rating == 0
        assert first_half_rating_degrees == 0
        assert second_half_rating_degrees == 0

    def test_get_rating_degrees_scenario2(self):
        rating = 1
        rating, first_half_rating_degrees, second_half_rating_degrees = get_rating_degrees(rating)
        assert rating == 1
        assert first_half_rating_degrees == 72
        assert second_half_rating_degrees == 0

    def test_get_rating_degrees_scenario3(self):
        rating = 2.5
        rating, first_half_rating_degrees, second_half_rating_degrees = get_rating_degrees(rating)
        assert rating == 2.5
        assert first_half_rating_degrees == 180
        assert second_half_rating_degrees == 0

    def test_get_rating_degrees_scenario4(self):
        rating = 3
        rating, first_half_rating_degrees, second_half_rating_degrees = get_rating_degrees(rating)
        assert rating == 3
        assert first_half_rating_degrees == 180
        assert second_half_rating_degrees == 36

    def test_get_rating_degrees_scenario5(self):
        rating = 4.12
        rating, first_half_rating_degrees, second_half_rating_degrees = get_rating_degrees(rating)
        assert rating == 4.12
        assert first_half_rating_degrees == 180
        assert second_half_rating_degrees == 116.63999999999999

    def test_get_rating_degrees_scenario6(self):
        rating = 5
        rating, first_half_rating_degrees, second_half_rating_degrees = get_rating_degrees(rating)
        assert rating == 5
        assert first_half_rating_degrees == 180
        assert second_half_rating_degrees == 180
