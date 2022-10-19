def group_elements(items, shape, menu_servers, item_back, item_next):
    num_count = len(items) - menu_servers
    num_items_count = shape[0] * shape[1]

    markup = []
    idx = menu_servers
    if len(items) < num_items_count:
        num_cols = (num_count - 1) // shape[0] + 1
        num_residue = num_cols * shape[0] - num_count
        row_limit = shape[0] - num_residue if num_count >= shape[0] else num_count
        if num_cols > 1:
            for _ in range(num_residue):
                markup_buttons = []
                for _ in range(num_cols - 1):
                    markup_buttons.append(items[idx])
                    idx += 1
                markup.append(markup_buttons)
        if num_cols > 0:
            for _ in range(row_limit):
                markup_buttons = []
                for _ in range(num_cols):
                    markup_buttons.append(items[idx])
                    idx += 1
                markup.append(markup_buttons)
    else:
        for _ in range(shape[0]):
            markup_buttons = []
            for _ in range(shape[1]):
                markup_buttons.append(items[idx])
                if idx >= len(items) - 1:
                    break
                idx += 1
            if markup_buttons:
                markup.append(markup_buttons)
            if idx >= len(items) - 1:
                break

    markup_bottom = []
    if menu_servers > 0:
        markup_bottom.append(item_back)
    if num_items_count < num_count:
        markup_bottom.append(item_next)
    if markup_bottom:
        markup.append(markup_bottom)
    return markup
