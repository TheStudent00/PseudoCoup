int64_t ui_pack_rect(int64_t x, int64_t y, int64_t w, int64_t h) {
    int64_t ux = (x & 65535);
    int64_t uy = ((y & 65535) << 16);
    int64_t uw = ((w & 65535) << 32);
    int64_t uh = ((h & 65535) << 48);
    return (((ux | uy) | uw) | uh);
}

int64_t ui_rect_lane(int64_t rect, int64_t lane) {
    int64_t shift = (((((lane & 3) * 16) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t raw = ((rect >> (shift & 63)) & 65535);
    return (((((raw ^ 32768) - 32768) & 4294967295) ^ 2147483648) - 2147483648);
}

int64_t ui_inset_rect(int64_t rect, int64_t pad_x, int64_t pad_y) {
    int64_t x = ((((ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648)) + pad_x) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t y = ((((ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648)) + pad_y) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t w = ((((ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_x * 2)) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t h = ((((ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_y * 2)) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t cw = (((((w > 0) ? w : 0) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t ch = (((((h > 0) ? h : 0) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(x, y, cw, ch);
}

int64_t ui_hit_test(int64_t rect, int64_t px, int64_t py) {
    int64_t x = ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t y = ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t w = ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t h = ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    if (((((px >= x) && (px < (x + w))) && (py >= y)) && (py < (y + h)))) {
        return (((1 & 4294967295) ^ 2147483648) - 2147483648);
    }
    return (((0 & 4294967295) ^ 2147483648) - 2147483648);
}

int64_t ui_intersect_rect(int64_t a, int64_t b) {
    int64_t ax0 = ui_rect_lane(a, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t ay0 = ui_rect_lane(a, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t ax1 = ((((ax0 + ui_rect_lane(a, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t ay1 = ((((ay0 + ui_rect_lane(a, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t bx0 = ui_rect_lane(b, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t by0 = ui_rect_lane(b, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t bx1 = ((((bx0 + ui_rect_lane(b, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t by1 = ((((by0 + ui_rect_lane(b, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t x0 = (((((ax0 > bx0) ? ax0 : bx0) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t y0 = (((((ay0 > by0) ? ay0 : by0) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t x1 = (((((ax1 < bx1) ? ax1 : bx1) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t y1 = (((((ay1 < by1) ? ay1 : by1) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(x0, y0, ((x1 > x0) ? (x1 - x0) : 0), ((y1 > y0) ? (y1 - y0) : 0));
}

int64_t ui_constrain_dim(int64_t val, int64_t min_v, int64_t max_v) {
    int64_t lo = ((val < min_v) ? min_v : val);
    return ((lo > max_v) ? max_v : lo);
}

int64_t ui_align_offset(int64_t container_len, int64_t child_len, int64_t align_mode) {
    int64_t slack = ((container_len > child_len) ? (container_len - child_len) : 0);
    if ((align_mode == 1)) {
        return (slack / 2);
    }
    if ((align_mode == 2)) {
        return slack;
    }
    return 0;
}

int64_t ui_flex_child_size(int64_t avail_main, int64_t fixed_sum, int64_t gap, int64_t flex0, int64_t flex1, int64_t flex2, int64_t child_idx) {
    int64_t raw_free = ((avail_main - fixed_sum) - (gap * 2));
    int64_t free_space = ((raw_free > 0) ? raw_free : 0);
    int64_t total_flex = ((flex0 + flex1) + flex2);
    if ((total_flex <= 0)) {
        return 0;
    }
    int64_t s0 = ((free_space * flex0) / total_flex);
    int64_t s1 = ((free_space * flex1) / total_flex);
    int64_t s2 = ((free_space - s0) - s1);
    return ((child_idx == 0) ? s0 : ((child_idx == 1) ? s1 : s2));
}

int64_t ui_layout_scaffold_box(int64_t viewport_rect, int64_t safe_top, int64_t safe_bottom, int64_t appbar_h, int64_t nav_h, int64_t section_idx) {
    int64_t vx = ui_rect_lane(viewport_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t vy = ui_rect_lane(viewport_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t vw = ui_rect_lane(viewport_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t vh = ui_rect_lane(viewport_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t inner_h = ((vh - safe_top) - safe_bottom);
    int64_t body_h = ui_flex_child_size(inner_h, (appbar_h + nav_h), 0, 0, 1, 0, 1);
    if ((section_idx == 0)) {
        return ui_pack_rect(vx, ((((vy + safe_top) & 4294967295) ^ 2147483648) - 2147483648), vw, (((appbar_h & 4294967295) ^ 2147483648) - 2147483648));
    }
    if ((section_idx == 1)) {
        return ui_pack_rect(vx, (((((vy + safe_top) + appbar_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((body_h & 4294967295) ^ 2147483648) - 2147483648));
    }
    return ui_pack_rect(vx, ((((((vy + safe_top) + appbar_h) + body_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((nav_h & 4294967295) ^ 2147483648) - 2147483648));
}

int64_t ui_layout_nav_tab(int64_t nav_rect, int64_t gap, int64_t tab_idx) {
    int64_t nx = ui_rect_lane(nav_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t ny = ui_rect_lane(nav_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t nw = ui_rect_lane(nav_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t nh = ui_rect_lane(nav_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t w0 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 0);
    int64_t w1 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 1);
    int64_t w2 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 2);
    int64_t tx = ((tab_idx == 0) ? nx : ((tab_idx == 1) ? ((nx + w0) + gap) : (((nx + w0) + w1) + (gap * 2))));
    int64_t tw = ((tab_idx == 0) ? w0 : ((tab_idx == 1) ? w1 : w2));
    return ui_pack_rect((((tx & 4294967295) ^ 2147483648) - 2147483648), ny, (((tw & 4294967295) ^ 2147483648) - 2147483648), nh);
}

int64_t ui_scroll_step(int64_t scroll_pos, int64_t velocity, int64_t drag_delta, int64_t max_scroll, int64_t bounce_ios) {
    int64_t raw_vel = ((((((velocity * 3) / 4) + drag_delta) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t raw_pos = ((((scroll_pos + raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
    if ((bounce_ios == 0)) {
        int64_t clamped_pos = ui_constrain_dim(raw_pos, 0, max_scroll);
        int64_t hit_edge = ((((((raw_pos < 0) || (raw_pos > max_scroll)) ? 1 : 0) & 4294967295) ^ 2147483648) - 2147483648);
        int64_t clamped_vel = (((((hit_edge == 1) ? 0 : raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
        return ui_pack_rect(clamped_pos, clamped_vel, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    }
    int64_t over_top = (((((raw_pos < 0) ? raw_pos : 0) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t over_bot = (((((raw_pos > max_scroll) ? (raw_pos - max_scroll) : 0) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t overscroll = ((((over_top + over_bot) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t spring_pull = ((((overscroll / 3) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t bounced_pos = ((((raw_pos - spring_pull) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t bounced_vel = (((((overscroll != 0) ? ((raw_vel - spring_pull) / 2) : raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(bounced_pos, bounced_vel, overscroll, (((0 & 4294967295) ^ 2147483648) - 2147483648));
}

int64_t ui_visible_card_index(int64_t scroll_pos, int64_t card_h, int64_t card_gap, int64_t total_cards) {
    int64_t stride = ((((card_h + card_gap) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t clamped_scroll = (((((scroll_pos < 0) ? 0 : scroll_pos) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t raw_idx = ((((clamped_scroll / stride) & 4294967295) ^ 2147483648) - 2147483648);
    return (((ui_constrain_dim(raw_idx, 0, (total_cards - 1)) & 4294967295) ^ 2147483648) - 2147483648);
}

int64_t ui_layout_list_card(int64_t body_rect, int64_t scroll_pos, int64_t card_h, int64_t card_gap, int64_t card_idx) {
    int64_t inner_body = ui_inset_rect(body_rect, (((12 & 4294967295) ^ 2147483648) - 2147483648), (((8 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t bx = ui_rect_lane(inner_body, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t by = ui_rect_lane(inner_body, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t bw = ui_rect_lane(inner_body, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t card_y = (((((by + (card_idx * (card_h + card_gap))) - scroll_pos) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t raw_card = ui_pack_rect(bx, card_y, bw, card_h);
    return ui_intersect_rect(raw_card, body_rect);
}

int64_t ui_hit_test_nav(int64_t nav_rect, int64_t gap, int64_t px, int64_t py) {
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

int64_t ui_dispatch_event(int64_t state, int64_t viewport_rect, int64_t ev_type, int64_t px, int64_t py, int64_t delta_y, int64_t bounce_ios) {
    int64_t active_tab = ui_rect_lane(state, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t sel_card = ui_rect_lane(state, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t scroll_pos = ui_rect_lane(state, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t scroll_vel = ui_rect_lane(state, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t safe_top = ((bounce_ios == 1) ? 48 : 24);
    int64_t safe_bot = ((bounce_ios == 1) ? 34 : 16);
    int64_t body_rect = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 1);
    int64_t nav_rect = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 2);
    if ((ev_type == 1)) {
        int64_t tapped_tab = ui_hit_test_nav(nav_rect, 8, px, py);
        if ((tapped_tab >= 0)) {
            return ui_pack_rect((((tapped_tab & 4294967295) ^ 2147483648) - 2147483648), sel_card, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
        }
        int64_t vis_idx = ui_visible_card_index(scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), (((20 & 4294967295) ^ 2147483648) - 2147483648));
        int64_t card_rect = ui_layout_list_card(body_rect, scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), vis_idx);
        int64_t new_sel = ((ui_hit_test(card_rect, (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1) ? vis_idx : sel_card);
        return ui_pack_rect(active_tab, (((new_sel & 4294967295) ^ 2147483648) - 2147483648), scroll_pos, scroll_vel);
    }
    int64_t step = ui_scroll_step(scroll_pos, scroll_vel, (((((ev_type == 2) ? delta_y : 0) & 4294967295) ^ 2147483648) - 2147483648), (((800 & 4294967295) ^ 2147483648) - 2147483648), (((bounce_ios & 4294967295) ^ 2147483648) - 2147483648));
    return ui_pack_rect(active_tab, sel_card, ui_rect_lane(step, (((0 & 4294967295) ^ 2147483648) - 2147483648)), ui_rect_lane(step, (((1 & 4294967295) ^ 2147483648) - 2147483648)));
}

int64_t ui_simulate_mobile_session(int64_t vw, int64_t vh, int64_t bounce_ios, int64_t gesture_delta) {
    int64_t vp = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((vw & 4294967295) ^ 2147483648) - 2147483648), (((vh & 4294967295) ^ 2147483648) - 2147483648));
    int64_t st = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((-1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    st = ui_dispatch_event(st, vp, 1, ((((vw ^ 2) < 0) && ((vw % 2) != 0)) ? ((vw / 2) - 1) : (vw / 2)), (vh - 40), 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 2, 0, 0, gesture_delta, bounce_ios);
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 1, ((((vw ^ 2) < 0) && ((vw % 2) != 0)) ? ((vw / 2) - 1) : (vw / 2)), 140, 0, bounce_ios);
    int64_t tab = ui_rect_lane(st, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t sel = ui_rect_lane(st, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t pos = ui_rect_lane(st, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t vel = ui_rect_lane(st, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    return ((((tab * 10000000) + (sel * 100000)) + (pos * 100)) + vel);
}
