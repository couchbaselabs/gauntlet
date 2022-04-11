class Queries:
    users_collection = "`e2e`.`profiles`.`users`"
    uri_collection = "e2e.stack.api_details"
    get_user_password = f"SELECT `password` FROM {users_collection} WHERE `username` = '{{0}}'"
    get_user_id = f"SELECT `id` FROM {users_collection} WHERE `username` = '{{0}}'"
    get_all_bookings = f"SELECT bookings FROM {users_collection} WHERE `username` = '{{0}}'"
    update_bookings = f"UPDATE {users_collection} SET bookings = ARRAY_APPEND(IFMISSING(bookings, []), '{{0}}') where username = '{{1}}'"
    get_api_details = f"SELECT host, port, username, `password`, method from {uri_collection} where service = '{{0}}' and uri = '{{1}}'"