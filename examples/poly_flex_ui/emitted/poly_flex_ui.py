def ui_pack_rect(x, y, w, h):
    ux = (x & 65535)
    uy = ((y & 65535) << 16)
    uw = ((w & 65535) << 32)
    uh = ((h & 65535) << 48)
    return (((ux | uy) | uw) | uh)

def ui_rect_lane(rect, lane):
    shift = (((((lane & 3) * 16) & 4294967295) ^ 2147483648) - 2147483648)
    raw = ((rect >> (shift & 63)) & 65535)
    return (((((raw ^ 32768) - 32768) & 4294967295) ^ 2147483648) - 2147483648)

def ui_inset_rect(rect, pad_x, pad_y):
    x = ((((ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648)) + pad_x) & 4294967295) ^ 2147483648) - 2147483648)
    y = ((((ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648)) + pad_y) & 4294967295) ^ 2147483648) - 2147483648)
    w = ((((ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_x * 2)) & 4294967295) ^ 2147483648) - 2147483648)
    h = ((((ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_y * 2)) & 4294967295) ^ 2147483648) - 2147483648)
    cw = ((((w if (w > 0) else 0) & 4294967295) ^ 2147483648) - 2147483648)
    ch = ((((h if (h > 0) else 0) & 4294967295) ^ 2147483648) - 2147483648)
    return ui_pack_rect(x, y, cw, ch)

def ui_hit_test(rect, px, py):
    x = ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    y = ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    w = ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    h = ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    if ((((px >= x) and (px < (x + w))) and (py >= y)) and (py < (y + h))):
        return (((1 & 4294967295) ^ 2147483648) - 2147483648)
    return (((0 & 4294967295) ^ 2147483648) - 2147483648)

def ui_intersect_rect(a, b):
    ax0 = ui_rect_lane(a, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    ay0 = ui_rect_lane(a, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    ax1 = ((((ax0 + ui_rect_lane(a, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648)
    ay1 = ((((ay0 + ui_rect_lane(a, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648)
    bx0 = ui_rect_lane(b, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    by0 = ui_rect_lane(b, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    bx1 = ((((bx0 + ui_rect_lane(b, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648)
    by1 = ((((by0 + ui_rect_lane(b, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648)
    x0 = ((((ax0 if (ax0 > bx0) else bx0) & 4294967295) ^ 2147483648) - 2147483648)
    y0 = ((((ay0 if (ay0 > by0) else by0) & 4294967295) ^ 2147483648) - 2147483648)
    x1 = ((((ax1 if (ax1 < bx1) else bx1) & 4294967295) ^ 2147483648) - 2147483648)
    y1 = ((((ay1 if (ay1 < by1) else by1) & 4294967295) ^ 2147483648) - 2147483648)
    return ui_pack_rect(x0, y0, ((x1 - x0) if (x1 > x0) else 0), ((y1 - y0) if (y1 > y0) else 0))

def ui_constrain_dim(val, min_v, max_v):
    lo = (min_v if (val < min_v) else val)
    return (max_v if (lo > max_v) else lo)

def ui_align_offset(container_len, child_len, align_mode):
    slack = ((container_len - child_len) if (container_len > child_len) else 0)
    if (align_mode == 1):
        return int(slack / 2)
    if (align_mode == 2):
        return slack
    return 0

def ui_flex_child_size(avail_main, fixed_sum, gap, flex0, flex1, flex2, child_idx):
    raw_free = ((avail_main - fixed_sum) - (gap * 2))
    free_space = (raw_free if (raw_free > 0) else 0)
    total_flex = ((flex0 + flex1) + flex2)
    if (total_flex <= 0):
        return 0
    s0 = int((free_space * flex0) / total_flex)
    s1 = int((free_space * flex1) / total_flex)
    s2 = ((free_space - s0) - s1)
    return (s0 if (child_idx == 0) else (s1 if (child_idx == 1) else s2))

def ui_layout_scaffold_box(viewport_rect, safe_top, safe_bottom, appbar_h, nav_h, section_idx):
    vx = ui_rect_lane(viewport_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    vy = ui_rect_lane(viewport_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    vw = ui_rect_lane(viewport_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    vh = ui_rect_lane(viewport_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    inner_h = ((vh - safe_top) - safe_bottom)
    body_h = ui_flex_child_size(inner_h, (appbar_h + nav_h), 0, 0, 1, 0, 1)
    if (section_idx == 0):
        return ui_pack_rect(vx, ((((vy + safe_top) & 4294967295) ^ 2147483648) - 2147483648), vw, (((appbar_h & 4294967295) ^ 2147483648) - 2147483648))
    if (section_idx == 1):
        return ui_pack_rect(vx, (((((vy + safe_top) + appbar_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((body_h & 4294967295) ^ 2147483648) - 2147483648))
    return ui_pack_rect(vx, ((((((vy + safe_top) + appbar_h) + body_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((nav_h & 4294967295) ^ 2147483648) - 2147483648))

def ui_layout_nav_tab(nav_rect, gap, tab_idx):
    nx = ui_rect_lane(nav_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    ny = ui_rect_lane(nav_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    nw = ui_rect_lane(nav_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    nh = ui_rect_lane(nav_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    w0 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 0)
    w1 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 1)
    w2 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 2)
    tx = (nx if (tab_idx == 0) else (((nx + w0) + gap) if (tab_idx == 1) else (((nx + w0) + w1) + (gap * 2))))
    tw = (w0 if (tab_idx == 0) else (w1 if (tab_idx == 1) else w2))
    return ui_pack_rect((((tx & 4294967295) ^ 2147483648) - 2147483648), ny, (((tw & 4294967295) ^ 2147483648) - 2147483648), nh)

def ui_scroll_step(scroll_pos, velocity, drag_delta, max_scroll, bounce_ios):
    raw_vel = ((((int((velocity * 3) / 4) + drag_delta) & 4294967295) ^ 2147483648) - 2147483648)
    raw_pos = ((((scroll_pos + raw_vel) & 4294967295) ^ 2147483648) - 2147483648)
    if (bounce_ios == 0):
        clamped_pos = ui_constrain_dim(raw_pos, 0, max_scroll)
        hit_edge = ((((1 if ((raw_pos < 0) or (raw_pos > max_scroll)) else 0) & 4294967295) ^ 2147483648) - 2147483648)
        clamped_vel = ((((0 if (hit_edge == 1) else raw_vel) & 4294967295) ^ 2147483648) - 2147483648)
        return ui_pack_rect(clamped_pos, clamped_vel, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648))
    over_top = ((((raw_pos if (raw_pos < 0) else 0) & 4294967295) ^ 2147483648) - 2147483648)
    over_bot = (((((raw_pos - max_scroll) if (raw_pos > max_scroll) else 0) & 4294967295) ^ 2147483648) - 2147483648)
    overscroll = ((((over_top + over_bot) & 4294967295) ^ 2147483648) - 2147483648)
    spring_pull = (((int(overscroll / 3) & 4294967295) ^ 2147483648) - 2147483648)
    bounced_pos = ((((raw_pos - spring_pull) & 4294967295) ^ 2147483648) - 2147483648)
    bounced_vel = ((((int((raw_vel - spring_pull) / 2) if (overscroll != 0) else raw_vel) & 4294967295) ^ 2147483648) - 2147483648)
    return ui_pack_rect(bounced_pos, bounced_vel, overscroll, (((0 & 4294967295) ^ 2147483648) - 2147483648))

def ui_visible_card_index(scroll_pos, card_h, card_gap, total_cards):
    stride = ((((card_h + card_gap) & 4294967295) ^ 2147483648) - 2147483648)
    clamped_scroll = ((((0 if (scroll_pos < 0) else scroll_pos) & 4294967295) ^ 2147483648) - 2147483648)
    raw_idx = (((int(clamped_scroll / stride) & 4294967295) ^ 2147483648) - 2147483648)
    return (((ui_constrain_dim(raw_idx, 0, (total_cards - 1)) & 4294967295) ^ 2147483648) - 2147483648)

def ui_layout_list_card(body_rect, scroll_pos, card_h, card_gap, card_idx):
    inner_body = ui_inset_rect(body_rect, (((12 & 4294967295) ^ 2147483648) - 2147483648), (((8 & 4294967295) ^ 2147483648) - 2147483648))
    bx = ui_rect_lane(inner_body, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    by = ui_rect_lane(inner_body, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    bw = ui_rect_lane(inner_body, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    card_y = (((((by + (card_idx * (card_h + card_gap))) - scroll_pos) & 4294967295) ^ 2147483648) - 2147483648)
    raw_card = ui_pack_rect(bx, card_y, bw, card_h)
    return ui_intersect_rect(raw_card, body_rect)

def ui_hit_test_nav(nav_rect, gap, px, py):
    if (ui_hit_test(ui_layout_nav_tab(nav_rect, gap, 0), (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1):
        return 0
    if (ui_hit_test(ui_layout_nav_tab(nav_rect, gap, 1), (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1):
        return 1
    if (ui_hit_test(ui_layout_nav_tab(nav_rect, gap, 2), (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1):
        return 2
    return -1

def ui_dispatch_event(state, viewport_rect, ev_type, px, py, delta_y, bounce_ios):
    active_tab = ui_rect_lane(state, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    sel_card = ui_rect_lane(state, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    scroll_pos = ui_rect_lane(state, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    scroll_vel = ui_rect_lane(state, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    safe_top = (48 if (bounce_ios == 1) else 24)
    safe_bot = (34 if (bounce_ios == 1) else 16)
    body_rect = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 1)
    nav_rect = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 2)
    if (ev_type == 1):
        tapped_tab = ui_hit_test_nav(nav_rect, 8, px, py)
        if (tapped_tab >= 0):
            return ui_pack_rect((((tapped_tab & 4294967295) ^ 2147483648) - 2147483648), sel_card, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648))
        vis_idx = ui_visible_card_index(scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), (((20 & 4294967295) ^ 2147483648) - 2147483648))
        card_rect = ui_layout_list_card(body_rect, scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), vis_idx)
        new_sel = (vis_idx if (ui_hit_test(card_rect, (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1) else sel_card)
        return ui_pack_rect(active_tab, (((new_sel & 4294967295) ^ 2147483648) - 2147483648), scroll_pos, scroll_vel)
    step = ui_scroll_step(scroll_pos, scroll_vel, ((((delta_y if (ev_type == 2) else 0) & 4294967295) ^ 2147483648) - 2147483648), (((800 & 4294967295) ^ 2147483648) - 2147483648), (((bounce_ios & 4294967295) ^ 2147483648) - 2147483648))
    return ui_pack_rect(active_tab, sel_card, ui_rect_lane(step, (((0 & 4294967295) ^ 2147483648) - 2147483648)), ui_rect_lane(step, (((1 & 4294967295) ^ 2147483648) - 2147483648)))

def ui_simulate_mobile_session(vw, vh, bounce_ios, gesture_delta):
    vp = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((vw & 4294967295) ^ 2147483648) - 2147483648), (((vh & 4294967295) ^ 2147483648) - 2147483648))
    st = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((-1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648))
    st = ui_dispatch_event(st, vp, 1, ((int(vw / 2) - 1) if (((vw ^ 2) < 0) and ((vw - (int(vw / 2) * 2)) != 0)) else int(vw / 2)), (vh - 40), 0, bounce_ios)
    st = ui_dispatch_event(st, vp, 2, 0, 0, gesture_delta, bounce_ios)
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios)
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios)
    st = ui_dispatch_event(st, vp, 1, ((int(vw / 2) - 1) if (((vw ^ 2) < 0) and ((vw - (int(vw / 2) * 2)) != 0)) else int(vw / 2)), 140, 0, bounce_ios)
    tab = ui_rect_lane(st, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    sel = ui_rect_lane(st, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    pos = ui_rect_lane(st, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    vel = ui_rect_lane(st, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    return ((((tab * 10000000) + (sel * 100000)) + (pos * 100)) + vel)
