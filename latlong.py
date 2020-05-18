import math

MAGIC_NUMBER = 111111


def get_search_centers(original_center, major_radius, minor_radius):
    """
    original_center : (float, float), latitude and longitude
    major_radius : float, search radius of entire area in meters
    minor_radius : float, search radius of smaller zones in meters

    returns [float], list new centers to use for search
    """

    result = []

    top_left = get_top_left_corner(original_center, major_radius)
    bottom_right = get_bottom_right_corner(original_center, major_radius)

    (top_left_latitude, top_left_longitude) = top_left
    start_latitude = move_down(top_left_latitude, minor_radius)
    start_longitude = move_right(top_left_latitude,
                                 top_left_longitude, minor_radius)
    # start at this point
    next_point = (start_latitude, start_longitude)

    while next_point:
        result.append((next_point))
        next_point = increment_point(next_point, top_left,
                                     bottom_right, minor_radius)

    return result


def increment_point(start_point, top_left, bottom_right, minor_radius):

    (orig_latitude, orig_longitude) = start_point
    (top_left_latitude, top_left_longitude) = top_left
    (bottom_right_latitude, bottom_right_longitude) = bottom_right

    hypotenuse_length = minor_radius * math.sqrt(2)

    # shift right
    candidate_longitude = move_right(orig_latitude,
                                     orig_longitude, hypotenuse_length)
    if candidate_longitude < bottom_right_longitude:
        return (orig_latitude, candidate_longitude)

    # exceeded right bound so go down a row
    candidate_latitude = move_down(orig_latitude, hypotenuse_length)
    if candidate_latitude > bottom_right_latitude:
        default_longitude = move_right(candidate_latitude,
                                       top_left_longitude, minor_radius)
        return (candidate_latitude, default_longitude)

    # exceeded lower bound so return None
    return None


def get_top_left_corner(original_center, radius):
    """
    original_center : (float, float), latitude and longitude
    radius : float, search radius in meters

    returns (float, float), top left corner latitude and longitude
    """

    (orig_latitude, orig_longitude) = original_center

    new_latitude = move_up(orig_latitude, radius)
    new_longitude = move_left(orig_latitude, orig_longitude, radius)

    return (new_latitude, new_longitude)


def get_bottom_right_corner(original_center, radius):
    """
    original_center : (float, float), latitude and longitude
    radius : float, search radius in meters

    returns (float, float), top left corner latitude and longitude
    """

    (orig_latitude, orig_longitude) = original_center

    new_latitude = move_down(orig_latitude, radius)
    new_longitude = move_right(orig_latitude, orig_longitude, radius)

    return (new_latitude, new_longitude)


def point_in_bounds(test_point, bottom_right):

    (test_latitude, test_longitude) = test_point
    (bound_latitude, bound_longitude) = bottom_right

    return test_latitude > bound_latitude and test_longitude > bound_longitude


def move_up(latitude, distance):
    """
    latitude : float, latitude
    distance : float, distance to move

    returns float, new latitude
    """

    return latitude + distance / MAGIC_NUMBER


def move_down(latitude, distance):
    """
    latitude : float, latitude
    distance : float, distance to move

    returns float, new latitude
    """

    return latitude - distance / MAGIC_NUMBER


def move_right(latitude, longitude, distance):
    """
    latitude : float, latitude
    longitude : float, longitude
    distance : float, search radius in meters

    returns float, new longitude
    """

    return longitude + (distance /
                        (MAGIC_NUMBER * math.cos(math.radians(latitude))))


def move_left(latitude, longitude, distance):
    """
    latitude : float, latitude
    longitude : float, longitude
    distance : float, search radius in meters

    returns float, new longitude
    """

    return longitude - (distance /
                        (MAGIC_NUMBER * math.cos(math.radians(latitude))))


def haversine_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371000 # m

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d


def main():

    centers = get_search_centers((48, -120), 2000, 500)
    for (i, point) in enumerate(centers):
        (latitude, longitude) = point
        print("{},{},{},#FF0000".format(latitude, longitude, i + 1))


if __name__ == "__main__":
    main()
