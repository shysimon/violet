class LikedItem(object):
    def __init__(self, user_id, item_type, item_id):
        self.user_id = user_id
        self.item_type = item_type
        self.item_id = item_id
        self.item_idx = -1
        self.composite_key = -1