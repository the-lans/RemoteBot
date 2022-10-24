def group_elements(items, shape, menu_servers, item_back, item_next, add_items=None):
    count = menu_servers * shape[0] * shape[1]
    num_count = len(items) - count
    num_items_count = shape[0] * shape[1]

    markup = []
    idx = count
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
                if idx >= len(items):
                    break
                markup_buttons.append(items[idx])
                idx += 1
            if markup_buttons:
                markup.append(markup_buttons)
            if idx >= len(items):
                break

    markup_bottom = []
    if menu_servers > 0:
        markup_bottom.append(item_back)
    if add_items:
        for item in add_items:
            markup_bottom.append(item)
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
    is_param2, is_param_new, is_param_new2 = False, False, False
    args, kwargs = [], {}
    for item in text_cmd:
        is_param_new = item[:1] == '-'
        is_param_new2 = item[:2] == '--'
        if is_param_new and not is_param_new2:
            param = get_param(item)
            kwargs[param] = True
        else:
            if is_param2:
                kwargs[param] = True if is_param_new else item
            if is_param_new2:
                item_equals = item.split('=')
                if len(item_equals) > 1:
                    param = get_param(item_equals[0])
                    kwargs[param] = item_equals[1]
                    is_param_new2 = False
                else:
                    param = get_param(item)
            elif not is_param2:
                args.append(item)
        is_param2 = is_param_new2
    return cmd, args, kwargs


def cmd_join(cmd, args, kwargs, bool_true=True, bool_false=True):
    dres = []
    for key, val in kwargs.items():
        if bool_true and isinstance(val, bool) and val:
            dres.append(f'-{key}')
        elif bool_false and isinstance(val, bool) and not val:
            pass
        else:
            dres.append(f'--{key} {val}')
    res = [cmd]
    if args:
        res.append(' '.join(args))
    if dres:
        res.append(' '.join(dres))
    return ' '.join(res)


def break_into_blocks(text: str, split_words: list):
    lines = text.split('\n')
    result = []
    block = []
    for line in lines:
        tline = line.strip()
        words = tline.split(' ')
        if tline:
            if words[0].lower() in split_words:
                if block:
                    result.append('\n'.join(block))
                    block = []
                result.append(tline)
            else:
                block.append(tline)
    if block:
        result.append('\n'.join(block))
    return result


def path_relative(path):
    return path[0] == '.'


def path_join(path1, path2, sys_type):
    sys_symbol = '\\' if sys_type == 'win' else '/'
    if sys_type == 'win':
        path1 = path1.replace('/', sys_symbol)
        path2 = path2.replace('/', sys_symbol)
    else:
        path1 = path1.replace('\\', sys_symbol)
        path2 = path2.replace('\\', sys_symbol)
    path1_arr = path1.split(sys_symbol)
    path2_arr = path2.split(sys_symbol)
    if path1_arr[-1] == '':
        path1_arr = path1_arr[:-1]
    if path2_arr[-1] == '':
        path2_arr = path2_arr[:-1]
    ind, idx_double = 0, 0
    while ind < len(path2_arr) and path2_arr[ind][0] == '.':
        if path2_arr[ind] == '..':
            idx_double += 1
        ind += 1
    if idx_double > 0:
        path1_arr = path1_arr[:-idx_double]
    if ind > 0:
        path2_arr = path2_arr[ind:]
    if path2_arr:
        return sys_symbol.join(path1_arr) + sys_symbol + sys_symbol.join(path2_arr)
    else:
        return sys_symbol.join(path1_arr)


def dict_to_str(data: dict, custom: str = '{0}: {1}') -> str:
    return '\n'.join([custom.format(key, val) for key, val in data.items()])


def str_del_startswith(val: str, template: str):
    if val.startswith(template):
        val = val[len(template) :]
    return val
