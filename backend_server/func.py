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


def file_write(name, data, is_append=False):
    with open(name, 'at' if is_append else 'wt') as fp:
        fp.write(data)


def file_read(name):
    with open(name, 'rt') as fp:
        data = fp.read()
    return data


def cmd_parser(text):
    def get_param(item):
        return item[2:] if item[:2] == '--' else item[1:]

    text_cmd = text.strip().split(' ')
    cmd = text_cmd[0]
    text_cmd = text_cmd[1:]
    is_param, is_param_new = False, False
    args, kwargs = [], {}
    for item in text_cmd:
        is_param_new = item[:1] == '-'
        if is_param:
            kwargs[param] = True if is_param_new else item
        if is_param_new:
            item_equals = item.split('=')
            if len(item_equals) > 1:
                param = get_param(item_equals[0])
                kwargs[param] = item_equals[1]
                is_param_new = False
            else:
                param = get_param(item)
        elif not is_param:
            args.append(item)
        is_param = is_param_new
    return cmd, args, kwargs


def cmd_join(cmd, args, kwargs, bool_true=False, bool_false=False):
    dres = []
    for key, val in kwargs.items():
        if bool_true and isinstance(val, bool) and val:
            dres.append(f'--{key}' if len(key) > 1 else f'-{key}')
        elif bool_false and isinstance(val, bool) and not val:
            pass
        else:
            dres.append(f'--{key} {val}' if len(key) > 1 else f'-{key} {val}')
    res = [cmd]
    if args:
        res.append(' '.join(args))
    if dres:
        res.append(' '.join(dres))
    return ' '.join(res)
