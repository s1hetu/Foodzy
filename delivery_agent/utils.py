def convert_timedelta(duration):
    if duration == 0:
        return "Not Available"
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)


def convert_into_star_rating(queryset, restaurant=None):
    for obj in queryset:
        rate = obj.ratings if restaurant else obj.rating
        val = str(float(str(rate))).split('.')
        res = [range(int(val[0]))]
        if val[1] == '0':
            res.append(range(0))
            res.append(range(5 - int(val[0])))
        else:
            res.append(range(1))
            res.append(range(4 - int(val[0])))

        if restaurant:
            res.append(obj.ratings)
            obj.ratings = res
        else:
            res.append(obj.rating)
            obj.rating = res

    return queryset


def get_rating_degrees(rating):
    if rating:
        rating_degrees = rating * (360 // 5)

        if rating_degrees <= 180:
            first_half_rating_degrees = rating_degrees
            second_half_rating_degrees = 0
        else:
            first_half_rating_degrees = 180
            second_half_rating_degrees = rating_degrees - 180
    else:
        rating = first_half_rating_degrees = second_half_rating_degrees = 0

    return rating, first_half_rating_degrees, second_half_rating_degrees
