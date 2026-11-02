fn ui_pack_rect(x: i64, y: i64, w: i64, h: i64) -> i64 {
    let mut ux: i64 = (x & 65535);
    let mut uy: i64 = ((y & 65535) << (16 & 63));
    let mut uw: i64 = ((w & 65535) << (32 & 63));
    let mut uh: i64 = ((h & 65535) << (48 & 63));
    return (((ux | uy) | uw) | uh);
}

fn ui_rect_lane(rect: i64, lane: i64) -> i64 {
    let mut shift: i64 = (((((lane & 3) * 16) & 4294967295) ^ 2147483648) - 2147483648);
    let mut raw: i64 = ((rect >> (shift & 63)) & 65535);
    return (((((raw ^ 32768) - 32768) & 4294967295) ^ 2147483648) - 2147483648);
}

fn ui_inset_rect(rect: i64, pad_x: i64, pad_y: i64) -> i64 {
    let mut x: i64 = ((((ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648)) + pad_x) & 4294967295) ^ 2147483648) - 2147483648);
    let mut y: i64 = ((((ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648)) + pad_y) & 4294967295) ^ 2147483648) - 2147483648);
    let mut w: i64 = ((((ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_x * 2)) & 4294967295) ^ 2147483648) - 2147483648);
    let mut h: i64 = ((((ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_y * 2)) & 4294967295) ^ 2147483648) - 2147483648);
    let mut cw: i64 = ((((if (w > 0) { w } else { 0 }) & 4294967295) ^ 2147483648) - 2147483648);
    let mut ch: i64 = ((((if (h > 0) { h } else { 0 }) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(x, y, cw, ch);
}

fn ui_hit_test(rect: i64, px: i64, py: i64) -> i64 {
    let mut x: i64 = ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let mut y: i64 = ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let mut w: i64 = ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let mut h: i64 = ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    if (((((px >= x) && (px < (x + w))) && (py >= y)) && (py < (y + h)))) {
        return (((1 & 4294967295) ^ 2147483648) - 2147483648);
    }
    return (((0 & 4294967295) ^ 2147483648) - 2147483648);
}

fn ui_intersect_rect(a: i64, b: i64) -> i64 {
    let mut ax0: i64 = ui_rect_lane(a, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let mut ay0: i64 = ui_rect_lane(a, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let mut ax1: i64 = ((((ax0 + ui_rect_lane(a, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    let mut ay1: i64 = ((((ay0 + ui_rect_lane(a, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    let mut bx0: i64 = ui_rect_lane(b, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let mut by0: i64 = ui_rect_lane(b, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let mut bx1: i64 = ((((bx0 + ui_rect_lane(b, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    let mut by1: i64 = ((((by0 + ui_rect_lane(b, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    let mut x0: i64 = ((((if (ax0 > bx0) { ax0 } else { bx0 }) & 4294967295) ^ 2147483648) - 2147483648);
    let mut y0: i64 = ((((if (ay0 > by0) { ay0 } else { by0 }) & 4294967295) ^ 2147483648) - 2147483648);
    let mut x1: i64 = ((((if (ax1 < bx1) { ax1 } else { bx1 }) & 4294967295) ^ 2147483648) - 2147483648);
    let mut y1: i64 = ((((if (ay1 < by1) { ay1 } else { by1 }) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(x0, y0, (if (x1 > x0) { (x1 - x0) } else { 0 }), (if (y1 > y0) { (y1 - y0) } else { 0 }));
}

fn ui_constrain_dim(val: i64, min_v: i64, max_v: i64) -> i64 {
    let mut lo: i64 = (if (val < min_v) { min_v } else { val });
    return (if (lo > max_v) { max_v } else { lo });
}

fn ui_align_offset(container_len: i64, child_len: i64, align_mode: i64) -> i64 {
    let mut slack: i64 = (if (container_len > child_len) { (container_len - child_len) } else { 0 });
    if ((align_mode == 1)) {
        return (slack / 2);
    }
    if ((align_mode == 2)) {
        return slack;
    }
    return 0;
}

fn ui_flex_child_size(avail_main: i64, fixed_sum: i64, gap: i64, flex0: i64, flex1: i64, flex2: i64, child_idx: i64) -> i64 {
    let mut raw_free: i64 = ((avail_main - fixed_sum) - (gap * 2));
    let mut free_space: i64 = (if (raw_free > 0) { raw_free } else { 0 });
    let mut total_flex: i64 = ((flex0 + flex1) + flex2);
    if ((total_flex <= 0)) {
        return 0;
    }
    let mut s0: i64 = (if (((free_space * flex0) == -9223372036854775808) && (total_flex == -1)) { -9223372036854775808 } else { ((free_space * flex0) / total_flex) });
    let mut s1: i64 = (if (((free_space * flex1) == -9223372036854775808) && (total_flex == -1)) { -9223372036854775808 } else { ((free_space * flex1) / total_flex) });
    let mut s2: i64 = ((free_space - s0) - s1);
    return (if (child_idx == 0) { s0 } else { (if (child_idx == 1) { s1 } else { s2 }) });
}

fn ui_layout_scaffold_box(viewport_rect: i64, safe_top: i64, safe_bottom: i64, appbar_h: i64, nav_h: i64, section_idx: i64) -> i64 {
    let mut vx: i64 = ui_rect_lane(viewport_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let mut vy: i64 = ui_rect_lane(viewport_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let mut vw: i64 = ui_rect_lane(viewport_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let mut vh: i64 = ui_rect_lane(viewport_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    let mut inner_h: i64 = ((vh - safe_top) - safe_bottom);
    let mut body_h: i64 = ui_flex_child_size(inner_h, (appbar_h + nav_h), 0, 0, 1, 0, 1);
    if ((section_idx == 0)) {
        return ui_pack_rect(vx, ((((vy + safe_top) & 4294967295) ^ 2147483648) - 2147483648), vw, (((appbar_h & 4294967295) ^ 2147483648) - 2147483648));
    }
    if ((section_idx == 1)) {
        return ui_pack_rect(vx, (((((vy + safe_top) + appbar_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((body_h & 4294967295) ^ 2147483648) - 2147483648));
    }
    return ui_pack_rect(vx, ((((((vy + safe_top) + appbar_h) + body_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((nav_h & 4294967295) ^ 2147483648) - 2147483648));
}

fn ui_layout_nav_tab(nav_rect: i64, gap: i64, tab_idx: i64) -> i64 {
    let mut nx: i64 = ui_rect_lane(nav_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let mut ny: i64 = ui_rect_lane(nav_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let mut nw: i64 = ui_rect_lane(nav_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let mut nh: i64 = ui_rect_lane(nav_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    let mut w0: i64 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 0);
    let mut w1: i64 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 1);
    let mut w2: i64 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 2);
    let mut tx: i64 = (if (tab_idx == 0) { nx } else { (if (tab_idx == 1) { ((nx + w0) + gap) } else { (((nx + w0) + w1) + (gap * 2)) }) });
    let mut tw: i64 = (if (tab_idx == 0) { w0 } else { (if (tab_idx == 1) { w1 } else { w2 }) });
    return ui_pack_rect((((tx & 4294967295) ^ 2147483648) - 2147483648), ny, (((tw & 4294967295) ^ 2147483648) - 2147483648), nh);
}

fn ui_scroll_step(scroll_pos: i64, velocity: i64, drag_delta: i64, max_scroll: i64, bounce_ios: i64) -> i64 {
    let mut raw_vel: i64 = (((((if (((velocity * 3) == -9223372036854775808) && (4 == -1)) { -9223372036854775808 } else { ((velocity * 3) / 4) }) + drag_delta) & 4294967295) ^ 2147483648) - 2147483648);
    let mut raw_pos: i64 = ((((scroll_pos + raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
    if ((bounce_ios == 0)) {
        let mut clamped_pos: i64 = ui_constrain_dim(raw_pos, 0, max_scroll);
        let mut hit_edge: i64 = ((((if ((raw_pos < 0) || (raw_pos > max_scroll)) { 1 } else { 0 }) & 4294967295) ^ 2147483648) - 2147483648);
        let mut clamped_vel: i64 = ((((if (hit_edge == 1) { 0 } else { raw_vel }) & 4294967295) ^ 2147483648) - 2147483648);
        return ui_pack_rect(clamped_pos, clamped_vel, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    }
    let mut over_top: i64 = ((((if (raw_pos < 0) { raw_pos } else { 0 }) & 4294967295) ^ 2147483648) - 2147483648);
    let mut over_bot: i64 = ((((if (raw_pos > max_scroll) { (raw_pos - max_scroll) } else { 0 }) & 4294967295) ^ 2147483648) - 2147483648);
    let mut overscroll: i64 = ((((over_top + over_bot) & 4294967295) ^ 2147483648) - 2147483648);
    let mut spring_pull: i64 = ((((if ((overscroll == -9223372036854775808) && (3 == -1)) { -9223372036854775808 } else { (overscroll / 3) }) & 4294967295) ^ 2147483648) - 2147483648);
    let mut bounced_pos: i64 = ((((raw_pos - spring_pull) & 4294967295) ^ 2147483648) - 2147483648);
    let mut bounced_vel: i64 = ((((if (overscroll != 0) { ((raw_vel - spring_pull) / 2) } else { raw_vel }) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(bounced_pos, bounced_vel, overscroll, (((0 & 4294967295) ^ 2147483648) - 2147483648));
}

fn ui_visible_card_index(scroll_pos: i64, card_h: i64, card_gap: i64, total_cards: i64) -> i64 {
    let mut stride: i64 = ((((card_h + card_gap) & 4294967295) ^ 2147483648) - 2147483648);
    let mut clamped_scroll: i64 = ((((if (scroll_pos < 0) { 0 } else { scroll_pos }) & 4294967295) ^ 2147483648) - 2147483648);
    let mut raw_idx: i64 = ((((if ((clamped_scroll == -9223372036854775808) && (stride == -1)) { -9223372036854775808 } else { (clamped_scroll / stride) }) & 4294967295) ^ 2147483648) - 2147483648);
    return (((ui_constrain_dim(raw_idx, 0, (total_cards - 1)) & 4294967295) ^ 2147483648) - 2147483648);
}

fn ui_layout_list_card(body_rect: i64, scroll_pos: i64, card_h: i64, card_gap: i64, card_idx: i64) -> i64 {
    let mut inner_body: i64 = ui_inset_rect(body_rect, (((12 & 4294967295) ^ 2147483648) - 2147483648), (((8 & 4294967295) ^ 2147483648) - 2147483648));
    let mut bx: i64 = ui_rect_lane(inner_body, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let mut by: i64 = ui_rect_lane(inner_body, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let mut bw: i64 = ui_rect_lane(inner_body, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let mut card_y: i64 = (((((by + (card_idx * (card_h + card_gap))) - scroll_pos) & 4294967295) ^ 2147483648) - 2147483648);
    let mut raw_card: i64 = ui_pack_rect(bx, card_y, bw, card_h);
    return ui_intersect_rect(raw_card, body_rect);
}

fn ui_hit_test_nav(nav_rect: i64, gap: i64, px: i64, py: i64) -> i64 {
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

fn ui_dispatch_event(state: i64, viewport_rect: i64, ev_type: i64, px: i64, py: i64, delta_y: i64, bounce_ios: i64) -> i64 {
    let mut active_tab: i64 = ui_rect_lane(state, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let mut sel_card: i64 = ui_rect_lane(state, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let mut scroll_pos: i64 = ui_rect_lane(state, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let mut scroll_vel: i64 = ui_rect_lane(state, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    let mut safe_top: i64 = (if (bounce_ios == 1) { 48 } else { 24 });
    let mut safe_bot: i64 = (if (bounce_ios == 1) { 34 } else { 16 });
    let mut body_rect: i64 = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 1);
    let mut nav_rect: i64 = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 2);
    if ((ev_type == 1)) {
        let mut tapped_tab: i64 = ui_hit_test_nav(nav_rect, 8, px, py);
        if ((tapped_tab >= 0)) {
            return ui_pack_rect((((tapped_tab & 4294967295) ^ 2147483648) - 2147483648), sel_card, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
        }
        let mut vis_idx: i64 = ui_visible_card_index(scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), (((20 & 4294967295) ^ 2147483648) - 2147483648));
        let mut card_rect: i64 = ui_layout_list_card(body_rect, scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), vis_idx);
        let mut new_sel: i64 = (if (ui_hit_test(card_rect, (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1) { vis_idx } else { sel_card });
        return ui_pack_rect(active_tab, (((new_sel & 4294967295) ^ 2147483648) - 2147483648), scroll_pos, scroll_vel);
    }
    let mut step: i64 = ui_scroll_step(scroll_pos, scroll_vel, ((((if (ev_type == 2) { delta_y } else { 0 }) & 4294967295) ^ 2147483648) - 2147483648), (((800 & 4294967295) ^ 2147483648) - 2147483648), (((bounce_ios & 4294967295) ^ 2147483648) - 2147483648));
    return ui_pack_rect(active_tab, sel_card, ui_rect_lane(step, (((0 & 4294967295) ^ 2147483648) - 2147483648)), ui_rect_lane(step, (((1 & 4294967295) ^ 2147483648) - 2147483648)));
}

fn ui_simulate_mobile_session(vw: i64, vh: i64, bounce_ios: i64, gesture_delta: i64) -> i64 {
    let mut vp: i64 = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((vw & 4294967295) ^ 2147483648) - 2147483648), (((vh & 4294967295) ^ 2147483648) - 2147483648));
    let mut st: i64 = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((-1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    st = ui_dispatch_event(st, vp, 1, (if (((vw ^ 2) < 0) && ((vw % 2) != 0)) { ((vw / 2) - 1) } else { (vw / 2) }), (vh - 40), 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 2, 0, 0, gesture_delta, bounce_ios);
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 1, (if (((vw ^ 2) < 0) && ((vw % 2) != 0)) { ((vw / 2) - 1) } else { (vw / 2) }), 140, 0, bounce_ios);
    let mut tab: i64 = ui_rect_lane(st, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let mut sel: i64 = ui_rect_lane(st, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let mut pos: i64 = ui_rect_lane(st, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let mut vel: i64 = ui_rect_lane(st, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    return ((((tab * 10000000) + (sel * 100000)) + (pos * 100)) + vel);
}
