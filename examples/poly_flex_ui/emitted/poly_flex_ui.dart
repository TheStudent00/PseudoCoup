int ui_pack_rect(int x, int y, int w, int h) {
    int ux = (x & 65535);
    int uy = ((y & 65535) << (16 & 63));
    int uw = ((w & 65535) << (32 & 63));
    int uh = ((h & 65535) << (48 & 63));
    return (((ux | uy) | uw) | uh);
}

int ui_rect_lane(int rect, int lane) {
    int shift = (((((lane & 3) * 16) & 4294967295) ^ 2147483648) - 2147483648);
    int raw = ((rect >> (shift & 63)) & 65535);
    return (((((raw ^ 32768) - 32768) & 4294967295) ^ 2147483648) - 2147483648);
}

int ui_inset_rect(int rect, int pad_x, int pad_y) {
    int x = ((((ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648)) + pad_x) & 4294967295) ^ 2147483648) - 2147483648);
    int y = ((((ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648)) + pad_y) & 4294967295) ^ 2147483648) - 2147483648);
    int w = ((((ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_x * 2)) & 4294967295) ^ 2147483648) - 2147483648);
    int h = ((((ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_y * 2)) & 4294967295) ^ 2147483648) - 2147483648);
    int cw = (((((w > 0) ? w : 0) & 4294967295) ^ 2147483648) - 2147483648);
    int ch = (((((h > 0) ? h : 0) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(x, y, cw, ch);
}

int ui_hit_test(int rect, int px, int py) {
    int x = ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int y = ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int w = ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int h = ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    if (((((px >= x) && (px < (x + w))) && (py >= y)) && (py < (y + h)))) {
        return (((1 & 4294967295) ^ 2147483648) - 2147483648);
    }
    return (((0 & 4294967295) ^ 2147483648) - 2147483648);
}

int ui_intersect_rect(int a, int b) {
    int ax0 = ui_rect_lane(a, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int ay0 = ui_rect_lane(a, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int ax1 = ((((ax0 + ui_rect_lane(a, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    int ay1 = ((((ay0 + ui_rect_lane(a, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    int bx0 = ui_rect_lane(b, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int by0 = ui_rect_lane(b, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int bx1 = ((((bx0 + ui_rect_lane(b, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    int by1 = ((((by0 + ui_rect_lane(b, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    int x0 = (((((ax0 > bx0) ? ax0 : bx0) & 4294967295) ^ 2147483648) - 2147483648);
    int y0 = (((((ay0 > by0) ? ay0 : by0) & 4294967295) ^ 2147483648) - 2147483648);
    int x1 = (((((ax1 < bx1) ? ax1 : bx1) & 4294967295) ^ 2147483648) - 2147483648);
    int y1 = (((((ay1 < by1) ? ay1 : by1) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(x0, y0, ((x1 > x0) ? (x1 - x0) : 0), ((y1 > y0) ? (y1 - y0) : 0));
}

int ui_constrain_dim(int val, int min_v, int max_v) {
    int lo = ((val < min_v) ? min_v : val);
    return ((lo > max_v) ? max_v : lo);
}

int ui_align_offset(int container_len, int child_len, int align_mode) {
    int slack = ((container_len > child_len) ? (container_len - child_len) : 0);
    if ((align_mode == 1)) {
        return (slack ~/ 2);
    }
    if ((align_mode == 2)) {
        return slack;
    }
    return 0;
}

int ui_flex_child_size(int avail_main, int fixed_sum, int gap, int flex0, int flex1, int flex2, int child_idx) {
    int raw_free = ((avail_main - fixed_sum) - (gap * 2));
    int free_space = ((raw_free > 0) ? raw_free : 0);
    int total_flex = ((flex0 + flex1) + flex2);
    if ((total_flex <= 0)) {
        return 0;
    }
    int s0 = ((((free_space * flex0) == -9223372036854775808) && (total_flex == -1)) ? -9223372036854775808 : ((free_space * flex0) ~/ total_flex));
    int s1 = ((((free_space * flex1) == -9223372036854775808) && (total_flex == -1)) ? -9223372036854775808 : ((free_space * flex1) ~/ total_flex));
    int s2 = ((free_space - s0) - s1);
    return ((child_idx == 0) ? s0 : ((child_idx == 1) ? s1 : s2));
}

int ui_layout_scaffold_box(int viewport_rect, int safe_top, int safe_bottom, int appbar_h, int nav_h, int section_idx) {
    int vx = ui_rect_lane(viewport_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int vy = ui_rect_lane(viewport_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int vw = ui_rect_lane(viewport_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int vh = ui_rect_lane(viewport_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    int inner_h = ((vh - safe_top) - safe_bottom);
    int body_h = ui_flex_child_size(inner_h, (appbar_h + nav_h), 0, 0, 1, 0, 1);
    if ((section_idx == 0)) {
        return ui_pack_rect(vx, ((((vy + safe_top) & 4294967295) ^ 2147483648) - 2147483648), vw, (((appbar_h & 4294967295) ^ 2147483648) - 2147483648));
    }
    if ((section_idx == 1)) {
        return ui_pack_rect(vx, (((((vy + safe_top) + appbar_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((body_h & 4294967295) ^ 2147483648) - 2147483648));
    }
    return ui_pack_rect(vx, ((((((vy + safe_top) + appbar_h) + body_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((nav_h & 4294967295) ^ 2147483648) - 2147483648));
}

int ui_layout_nav_tab(int nav_rect, int gap, int tab_idx) {
    int nx = ui_rect_lane(nav_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int ny = ui_rect_lane(nav_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int nw = ui_rect_lane(nav_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int nh = ui_rect_lane(nav_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    int w0 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 0);
    int w1 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 1);
    int w2 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 2);
    int tx = ((tab_idx == 0) ? nx : ((tab_idx == 1) ? ((nx + w0) + gap) : (((nx + w0) + w1) + (gap * 2))));
    int tw = ((tab_idx == 0) ? w0 : ((tab_idx == 1) ? w1 : w2));
    return ui_pack_rect((((tx & 4294967295) ^ 2147483648) - 2147483648), ny, (((tw & 4294967295) ^ 2147483648) - 2147483648), nh);
}

int ui_scroll_step(int scroll_pos, int velocity, int drag_delta, int max_scroll, int bounce_ios) {
    int raw_vel = ((((((((velocity * 3) == -9223372036854775808) && (4 == -1)) ? -9223372036854775808 : ((velocity * 3) ~/ 4)) + drag_delta) & 4294967295) ^ 2147483648) - 2147483648);
    int raw_pos = ((((scroll_pos + raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
    if ((bounce_ios == 0)) {
        int clamped_pos = ui_constrain_dim(raw_pos, 0, max_scroll);
        int hit_edge = ((((((raw_pos < 0) || (raw_pos > max_scroll)) ? 1 : 0) & 4294967295) ^ 2147483648) - 2147483648);
        int clamped_vel = (((((hit_edge == 1) ? 0 : raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
        return ui_pack_rect(clamped_pos, clamped_vel, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    }
    int over_top = (((((raw_pos < 0) ? raw_pos : 0) & 4294967295) ^ 2147483648) - 2147483648);
    int over_bot = (((((raw_pos > max_scroll) ? (raw_pos - max_scroll) : 0) & 4294967295) ^ 2147483648) - 2147483648);
    int overscroll = ((((over_top + over_bot) & 4294967295) ^ 2147483648) - 2147483648);
    int spring_pull = ((((((overscroll == -9223372036854775808) && (3 == -1)) ? -9223372036854775808 : (overscroll ~/ 3)) & 4294967295) ^ 2147483648) - 2147483648);
    int bounced_pos = ((((raw_pos - spring_pull) & 4294967295) ^ 2147483648) - 2147483648);
    int bounced_vel = (((((overscroll != 0) ? ((raw_vel - spring_pull) ~/ 2) : raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(bounced_pos, bounced_vel, overscroll, (((0 & 4294967295) ^ 2147483648) - 2147483648));
}

int ui_visible_card_index(int scroll_pos, int card_h, int card_gap, int total_cards) {
    int stride = ((((card_h + card_gap) & 4294967295) ^ 2147483648) - 2147483648);
    int clamped_scroll = (((((scroll_pos < 0) ? 0 : scroll_pos) & 4294967295) ^ 2147483648) - 2147483648);
    int raw_idx = ((((((clamped_scroll == -9223372036854775808) && (stride == -1)) ? -9223372036854775808 : (clamped_scroll ~/ stride)) & 4294967295) ^ 2147483648) - 2147483648);
    return (((ui_constrain_dim(raw_idx, 0, (total_cards - 1)) & 4294967295) ^ 2147483648) - 2147483648);
}

int ui_layout_list_card(int body_rect, int scroll_pos, int card_h, int card_gap, int card_idx) {
    int inner_body = ui_inset_rect(body_rect, (((12 & 4294967295) ^ 2147483648) - 2147483648), (((8 & 4294967295) ^ 2147483648) - 2147483648));
    int bx = ui_rect_lane(inner_body, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int by = ui_rect_lane(inner_body, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int bw = ui_rect_lane(inner_body, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int card_y = (((((by + (card_idx * (card_h + card_gap))) - scroll_pos) & 4294967295) ^ 2147483648) - 2147483648);
    int raw_card = ui_pack_rect(bx, card_y, bw, card_h);
    return ui_intersect_rect(raw_card, body_rect);
}

int ui_hit_test_nav(int nav_rect, int gap, int px, int py) {
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

int ui_dispatch_event(int state, int viewport_rect, int ev_type, int px, int py, int delta_y, int bounce_ios) {
    int active_tab = ui_rect_lane(state, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int sel_card = ui_rect_lane(state, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int scroll_pos = ui_rect_lane(state, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int scroll_vel = ui_rect_lane(state, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    int safe_top = ((bounce_ios == 1) ? 48 : 24);
    int safe_bot = ((bounce_ios == 1) ? 34 : 16);
    int body_rect = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 1);
    int nav_rect = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 2);
    if ((ev_type == 1)) {
        int tapped_tab = ui_hit_test_nav(nav_rect, 8, px, py);
        if ((tapped_tab >= 0)) {
            return ui_pack_rect((((tapped_tab & 4294967295) ^ 2147483648) - 2147483648), sel_card, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
        }
        int vis_idx = ui_visible_card_index(scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), (((20 & 4294967295) ^ 2147483648) - 2147483648));
        int card_rect = ui_layout_list_card(body_rect, scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), vis_idx);
        int new_sel = ((ui_hit_test(card_rect, (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1) ? vis_idx : sel_card);
        return ui_pack_rect(active_tab, (((new_sel & 4294967295) ^ 2147483648) - 2147483648), scroll_pos, scroll_vel);
    }
    int step = ui_scroll_step(scroll_pos, scroll_vel, (((((ev_type == 2) ? delta_y : 0) & 4294967295) ^ 2147483648) - 2147483648), (((800 & 4294967295) ^ 2147483648) - 2147483648), (((bounce_ios & 4294967295) ^ 2147483648) - 2147483648));
    return ui_pack_rect(active_tab, sel_card, ui_rect_lane(step, (((0 & 4294967295) ^ 2147483648) - 2147483648)), ui_rect_lane(step, (((1 & 4294967295) ^ 2147483648) - 2147483648)));
}

int ui_simulate_mobile_session(int vw, int vh, int bounce_ios, int gesture_delta) {
    int vp = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((vw & 4294967295) ^ 2147483648) - 2147483648), (((vh & 4294967295) ^ 2147483648) - 2147483648));
    int st = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((-1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    st = ui_dispatch_event(st, vp, 1, ((((vw ^ 2) < 0) && ((vw.remainder(2)) != 0)) ? ((vw ~/ 2) - 1) : (vw ~/ 2)), (vh - 40), 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 2, 0, 0, gesture_delta, bounce_ios);
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 1, ((((vw ^ 2) < 0) && ((vw.remainder(2)) != 0)) ? ((vw ~/ 2) - 1) : (vw ~/ 2)), 140, 0, bounce_ios);
    int tab = ui_rect_lane(st, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int sel = ui_rect_lane(st, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int pos = ui_rect_lane(st, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int vel = ui_rect_lane(st, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    return ((((tab * 10000000) + (sel * 100000)) + (pos * 100)) + vel);
}
