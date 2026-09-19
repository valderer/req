def extract_cart_items(cart_data, section):
    """兼容 valid_cart 分组结构和 invalid_cart 直接列表结构。"""
    if not isinstance(cart_data, dict):
        return []

    cart_items = cart_data.get(section, [])
    if section == "invalid_cart":
        return cart_items

    return [
        item
        for group in cart_items
        for item in group.get("list", [])
    ]


def find_cart(cart_data, cart_id, section=None):
    """根据 cart_id 在指定区域或整个购物车中查找商品。"""
    sections = [section] if section else ["valid_cart", "invalid_cart"]
    items = [
        item
        for current_section in sections
        for item in extract_cart_items(cart_data, current_section)
    ]
    return next(
        (
            item
            for item in items
            if str(item.get("cart_id")) == str(cart_id)
        ),
        None,
    )
