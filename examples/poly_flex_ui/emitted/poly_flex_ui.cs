long ui_pack_rect(long x, long y, long w, long h) {
    long ux = (x & 65535);
    long uy = ((y & 65535) << 16);
    long uw = ((w & 65535) << 32);
    long uh = ((h & 65535) << 48);
    return (((ux | uy) | uw) | uh);
}

long ui_rect_lane(long rect, long lane) {
    long shift = (((((lane & 3) * 16) & 4294967295) ^ 2147483648) - 2147483648);
    long raw = ((rect >> (shift & 63)) & 65535);
    return (((((raw ^ 32768) - 32768) & 4294967295) ^ 2147483648) - 2147483648);
}

long ui_inset_rect(long rect, long pad_x, long pad_y) {
    long x = ((((ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648)) + pad_x) & 4294967295) ^ 2147483648) - 2147483648);
    long y = ((((ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648)) + pad_y) & 4294967295) ^ 2147483648) - 2147483648);
    long w = ((((ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_x * 2)) & 4294967295) ^ 2147483648) - 2147483648);
    long h = ((((ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_y * 2)) & 4294967295) ^ 2147483648) - 2147483648);
    long cw = (((((w > 0) ? w : 0) & 4294967295) ^ 2147483648) - 2147483648);
    long ch = (((((h > 0) ? h : 0) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(x, y, cw, ch);
}

long ui_hit_test(long rect, long px, long py) {
    long x = ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    long y = ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    long w = ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    long h = ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    if (((((px >= x) && (px < (x + w))) && (py >= y)) && (py < (y + h)))) {
        return (((1 & 4294967295) ^ 2147483648) - 2147483648);
    }
    return (((0 & 4294967295) ^ 2147483648) - 2147483648);
}

long ui_intersect_rect(long a, long b) {
    long ax0 = ui_rect_lane(a, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    long ay0 = ui_rect_lane(a, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    long ax1 = ((((ax0 + ui_rect_lane(a, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    long ay1 = ((((ay0 + ui_rect_lane(a, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    long bx0 = ui_rect_lane(b, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    long by0 = ui_rect_lane(b, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    long bx1 = ((((bx0 + ui_rect_lane(b, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    long by1 = ((((by0 + ui_rect_lane(b, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    long x0 = (((((ax0 > bx0) ? ax0 : bx0) & 4294967295) ^ 2147483648) - 2147483648);
    long y0 = (((((ay0 > by0) ? ay0 : by0) & 4294967295) ^ 2147483648) - 2147483648);
    long x1 = (((((ax1 < bx1) ? ax1 : bx1) & 4294967295) ^ 2147483648) - 2147483648);
    long y1 = (((((ay1 < by1) ? ay1 : by1) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(x0, y0, ((x1 > x0) ? (x1 - x0) : 0), ((y1 > y0) ? (y1 - y0) : 0));
}

long ui_constrain_dim(long val, long min_v, long max_v) {
    long lo = ((val < min_v) ? min_v : val);
    return ((lo > max_v) ? max_v : lo);
}

long ui_align_offset(long container_len, long child_len, long align_mode) {
    long slack = ((container_len > child_len) ? (container_len - child_len) : 0);
    if ((align_mode == 1)) {
        return (slack / 2);
    }
    if ((align_mode == 2)) {
        return slack;
    }
    return 0;
}

long ui_flex_child_size(long avail_main, long fixed_sum, long gap, long flex0, long flex1, long flex2, long child_idx) {
    long raw_free = ((avail_main - fixed_sum) - (gap * 2));
    long free_space = ((raw_free > 0) ? raw_free : 0);
    long total_flex = ((flex0 + flex1) + flex2);
    if ((total_flex <= 0)) {
        return 0;
    }
    long s0 = ((free_space * flex0) / total_flex);
    long s1 = ((free_space * flex1) / total_flex);
    long s2 = ((free_space - s0) - s1);
    return ((child_idx == 0) ? s0 : ((child_idx == 1) ? s1 : s2));
}

long ui_layout_scaffold_box(long viewport_rect, long safe_top, long safe_bottom, long appbar_h, long nav_h, long section_idx) {
    long vx = ui_rect_lane(viewport_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    long vy = ui_rect_lane(viewport_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    long vw = ui_rect_lane(viewport_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    long vh = ui_rect_lane(viewport_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    long inner_h = ((vh - safe_top) - safe_bottom);
    long body_h = ui_flex_child_size(inner_h, (appbar_h + nav_h), 0, 0, 1, 0, 1);
    if ((section_idx == 0)) {
        return ui_pack_rect(vx, ((((vy + safe_top) & 4294967295) ^ 2147483648) - 2147483648), vw, (((appbar_h & 4294967295) ^ 2147483648) - 2147483648));
    }
    if ((section_idx == 1)) {
        return ui_pack_rect(vx, (((((vy + safe_top) + appbar_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((body_h & 4294967295) ^ 2147483648) - 2147483648));
    }
    return ui_pack_rect(vx, ((((((vy + safe_top) + appbar_h) + body_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((nav_h & 4294967295) ^ 2147483648) - 2147483648));
}

long ui_layout_nav_tab(long nav_rect, long gap, long tab_idx) {
    long nx = ui_rect_lane(nav_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    long ny = ui_rect_lane(nav_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    long nw = ui_rect_lane(nav_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    long nh = ui_rect_lane(nav_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    long w0 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 0);
    long w1 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 1);
    long w2 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 2);
    long tx = ((tab_idx == 0) ? nx : ((tab_idx == 1) ? ((nx + w0) + gap) : (((nx + w0) + w1) + (gap * 2))));
    long tw = ((tab_idx == 0) ? w0 : ((tab_idx == 1) ? w1 : w2));
    return ui_pack_rect((((tx & 4294967295) ^ 2147483648) - 2147483648), ny, (((tw & 4294967295) ^ 2147483648) - 2147483648), nh);
}

long ui_scroll_step(long scroll_pos, long velocity, long drag_delta, long max_scroll, long bounce_ios) {
    long raw_vel = ((((((velocity * 3) / 4) + drag_delta) & 4294967295) ^ 2147483648) - 2147483648);
    long raw_pos = ((((scroll_pos + raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
    if ((bounce_ios == 0)) {
        long clamped_pos = ui_constrain_dim(raw_pos, 0, max_scroll);
        long hit_edge = ((((((raw_pos < 0) || (raw_pos > max_scroll)) ? 1 : 0) & 4294967295) ^ 2147483648) - 2147483648);
        long clamped_vel = (((((hit_edge == 1) ? 0 : raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
        return ui_pack_rect(clamped_pos, clamped_vel, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    }
    long over_top = (((((raw_pos < 0) ? raw_pos : 0) & 4294967295) ^ 2147483648) - 2147483648);
    long over_bot = (((((raw_pos > max_scroll) ? (raw_pos - max_scroll) : 0) & 4294967295) ^ 2147483648) - 2147483648);
    long overscroll = ((((over_top + over_bot) & 4294967295) ^ 2147483648) - 2147483648);
    long spring_pull = ((((overscroll / 3) & 4294967295) ^ 2147483648) - 2147483648);
    long bounced_pos = ((((raw_pos - spring_pull) & 4294967295) ^ 2147483648) - 2147483648);
    long bounced_vel = (((((overscroll != 0) ? ((raw_vel - spring_pull) / 2) : raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(bounced_pos, bounced_vel, overscroll, (((0 & 4294967295) ^ 2147483648) - 2147483648));
}

long ui_visible_card_index(long scroll_pos, long card_h, long card_gap, long total_cards) {
    long stride = ((((card_h + card_gap) & 4294967295) ^ 2147483648) - 2147483648);
    long clamped_scroll = (((((scroll_pos < 0) ? 0 : scroll_pos) & 4294967295) ^ 2147483648) - 2147483648);
    long raw_idx = ((((clamped_scroll / stride) & 4294967295) ^ 2147483648) - 2147483648);
    return (((ui_constrain_dim(raw_idx, 0, (total_cards - 1)) & 4294967295) ^ 2147483648) - 2147483648);
}

long ui_layout_list_card(long body_rect, long scroll_pos, long card_h, long card_gap, long card_idx) {
    long inner_body = ui_inset_rect(body_rect, (((12 & 4294967295) ^ 2147483648) - 2147483648), (((8 & 4294967295) ^ 2147483648) - 2147483648));
    long bx = ui_rect_lane(inner_body, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    long by = ui_rect_lane(inner_body, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    long bw = ui_rect_lane(inner_body, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    long card_y = (((((by + (card_idx * (card_h + card_gap))) - scroll_pos) & 4294967295) ^ 2147483648) - 2147483648);
    long raw_card = ui_pack_rect(bx, card_y, bw, card_h);
    return ui_intersect_rect(raw_card, body_rect);
}

long ui_hit_test_nav(long nav_rect, long gap, long px, long py) {
    if ((ui_hit_test(ui_layout_nav_tab(nav_rect, gap, 0), (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1)) {
        return 0;
    }
    if ((ui_hit_test(ui_layout_nav_tab(nav_rect, gap, 1), (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1)) {
        return 1;
    }
    if ((ui_hit_test(ui_layout_nav_tab(nav_rect, gap, 2), (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1)) {
        return 2;
    }
    return -1;
}

long ui_dispatch_event(long state, long viewport_rect, long ev_type, long px, long py, long delta_y, long bounce_ios) {
    long active_tab = ui_rect_lane(state, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    long sel_card = ui_rect_lane(state, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    long scroll_pos = ui_rect_lane(state, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    long scroll_vel = ui_rect_lane(state, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    long safe_top = ((bounce_ios == 1) ? 48 : 24);
    long safe_bot = ((bounce_ios == 1) ? 34 : 16);
    long body_rect = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 1);
    long nav_rect = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 2);
    if ((ev_type == 1)) {
        long tapped_tab = ui_hit_test_nav(nav_rect, 8, px, py);
        if ((tapped_tab >= 0)) {
            return ui_pack_rect((((tapped_tab & 4294967295) ^ 2147483648) - 2147483648), sel_card, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
        }
        long vis_idx = ui_visible_card_index(scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), (((20 & 4294967295) ^ 2147483648) - 2147483648));
        long card_rect = ui_layout_list_card(body_rect, scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), vis_idx);
        long new_sel = ((ui_hit_test(card_rect, (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1) ? vis_idx : sel_card);
        return ui_pack_rect(active_tab, (((new_sel & 4294967295) ^ 2147483648) - 2147483648), scroll_pos, scroll_vel);
    }
    long step = ui_scroll_step(scroll_pos, scroll_vel, (((((ev_type == 2) ? delta_y : 0) & 4294967295) ^ 2147483648) - 2147483648), (((800 & 4294967295) ^ 2147483648) - 2147483648), (((bounce_ios & 4294967295) ^ 2147483648) - 2147483648));
    return ui_pack_rect(active_tab, sel_card, ui_rect_lane(step, (((0 & 4294967295) ^ 2147483648) - 2147483648)), ui_rect_lane(step, (((1 & 4294967295) ^ 2147483648) - 2147483648)));
}

long ui_simulate_mobile_session(long vw, long vh, long bounce_ios, long gesture_delta) {
    long vp = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((vw & 4294967295) ^ 2147483648) - 2147483648), (((vh & 4294967295) ^ 2147483648) - 2147483648));
    long st = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((-1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    st = ui_dispatch_event(st, vp, 1, ((((vw ^ 2) < 0) && ((vw % 2) != 0)) ? ((vw / 2) - 1) : (vw / 2)), (vh - 40), 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 2, 0, 0, gesture_delta, bounce_ios);
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 1, ((((vw ^ 2) < 0) && ((vw % 2) != 0)) ? ((vw / 2) - 1) : (vw / 2)), 140, 0, bounce_ios);
    long tab = ui_rect_lane(st, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    long sel = ui_rect_lane(st, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    long pos = ui_rect_lane(st, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    long vel = ui_rect_lane(st, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    return ((((tab * 10000000) + (sel * 100000)) + (pos * 100)) + vel);
}
