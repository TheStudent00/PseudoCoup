function ui_pack_rect(x: number, y: number, w: number, h: number): number {
    let ux: number = (x & 65535);
    let uy: number = ((y & 65535) << (16 & 63));
    let uw: number = ((w & 65535) << (32 & 63));
    let uh: number = ((h & 65535) << (48 & 63));
    return (((ux | uy) | uw) | uh);
}

function ui_rect_lane(rect: number, lane: number): number {
    let shift: number = (((((lane & 3) * 16) & 4294967295) ^ 2147483648) - 2147483648);
    let raw: number = ((rect >> (shift & 63)) & 65535);
    return (((((raw ^ 32768) - 32768) & 4294967295) ^ 2147483648) - 2147483648);
}

function ui_inset_rect(rect: number, pad_x: number, pad_y: number): number {
    let x: number = ((((ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648)) + pad_x) & 4294967295) ^ 2147483648) - 2147483648);
    let y: number = ((((ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648)) + pad_y) & 4294967295) ^ 2147483648) - 2147483648);
    let w: number = ((((ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_x * 2)) & 4294967295) ^ 2147483648) - 2147483648);
    let h: number = ((((ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_y * 2)) & 4294967295) ^ 2147483648) - 2147483648);
    let cw: number = (((((w > 0) ? w : 0) & 4294967295) ^ 2147483648) - 2147483648);
    let ch: number = (((((h > 0) ? h : 0) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(x, y, cw, ch);
}

function ui_hit_test(rect: number, px: number, py: number): number {
    let x: number = ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let y: number = ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let w: number = ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let h: number = ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    if (((((px >= x) && (px < (x + w))) && (py >= y)) && (py < (y + h)))) {
        return (((1 & 4294967295) ^ 2147483648) - 2147483648);
    }
    return (((0 & 4294967295) ^ 2147483648) - 2147483648);
}

function ui_intersect_rect(a: number, b: number): number {
    let ax0: number = ui_rect_lane(a, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let ay0: number = ui_rect_lane(a, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let ax1: number = ((((ax0 + ui_rect_lane(a, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    let ay1: number = ((((ay0 + ui_rect_lane(a, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    let bx0: number = ui_rect_lane(b, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let by0: number = ui_rect_lane(b, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let bx1: number = ((((bx0 + ui_rect_lane(b, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    let by1: number = ((((by0 + ui_rect_lane(b, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648);
    let x0: number = (((((ax0 > bx0) ? ax0 : bx0) & 4294967295) ^ 2147483648) - 2147483648);
    let y0: number = (((((ay0 > by0) ? ay0 : by0) & 4294967295) ^ 2147483648) - 2147483648);
    let x1: number = (((((ax1 < bx1) ? ax1 : bx1) & 4294967295) ^ 2147483648) - 2147483648);
    let y1: number = (((((ay1 < by1) ? ay1 : by1) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(x0, y0, ((x1 > x0) ? (x1 - x0) : 0), ((y1 > y0) ? (y1 - y0) : 0));
}

function ui_constrain_dim(val: number, min_v: number, max_v: number): number {
    let lo: number = ((val < min_v) ? min_v : val);
    return ((lo > max_v) ? max_v : lo);
}

function ui_align_offset(container_len: number, child_len: number, align_mode: number): number {
    let slack: number = ((container_len > child_len) ? (container_len - child_len) : 0);
    if ((align_mode == 1)) {
        return Math.trunc(slack / 2);
    }
    if ((align_mode == 2)) {
        return slack;
    }
    return 0;
}

function ui_flex_child_size(avail_main: number, fixed_sum: number, gap: number, flex0: number, flex1: number, flex2: number, child_idx: number): number {
    let raw_free: number = ((avail_main - fixed_sum) - (gap * 2));
    let free_space: number = ((raw_free > 0) ? raw_free : 0);
    let total_flex: number = ((flex0 + flex1) + flex2);
    if ((total_flex <= 0)) {
        return 0;
    }
    let s0: number = ((((free_space * flex0) == -9223372036854775808) && (total_flex == -1)) ? -9223372036854775808 : Math.trunc((free_space * flex0) / total_flex));
    let s1: number = ((((free_space * flex1) == -9223372036854775808) && (total_flex == -1)) ? -9223372036854775808 : Math.trunc((free_space * flex1) / total_flex));
    let s2: number = ((free_space - s0) - s1);
    return ((child_idx == 0) ? s0 : ((child_idx == 1) ? s1 : s2));
}

function ui_layout_scaffold_box(viewport_rect: number, safe_top: number, safe_bottom: number, appbar_h: number, nav_h: number, section_idx: number): number {
    let vx: number = ui_rect_lane(viewport_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let vy: number = ui_rect_lane(viewport_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let vw: number = ui_rect_lane(viewport_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let vh: number = ui_rect_lane(viewport_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    let inner_h: number = ((vh - safe_top) - safe_bottom);
    let body_h: number = ui_flex_child_size(inner_h, (appbar_h + nav_h), 0, 0, 1, 0, 1);
    if ((section_idx == 0)) {
        return ui_pack_rect(vx, ((((vy + safe_top) & 4294967295) ^ 2147483648) - 2147483648), vw, (((appbar_h & 4294967295) ^ 2147483648) - 2147483648));
    }
    if ((section_idx == 1)) {
        return ui_pack_rect(vx, (((((vy + safe_top) + appbar_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((body_h & 4294967295) ^ 2147483648) - 2147483648));
    }
    return ui_pack_rect(vx, ((((((vy + safe_top) + appbar_h) + body_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((nav_h & 4294967295) ^ 2147483648) - 2147483648));
}

function ui_layout_nav_tab(nav_rect: number, gap: number, tab_idx: number): number {
    let nx: number = ui_rect_lane(nav_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let ny: number = ui_rect_lane(nav_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let nw: number = ui_rect_lane(nav_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let nh: number = ui_rect_lane(nav_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    let w0: number = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 0);
    let w1: number = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 1);
    let w2: number = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 2);
    let tx: number = ((tab_idx == 0) ? nx : ((tab_idx == 1) ? ((nx + w0) + gap) : (((nx + w0) + w1) + (gap * 2))));
    let tw: number = ((tab_idx == 0) ? w0 : ((tab_idx == 1) ? w1 : w2));
    return ui_pack_rect((((tx & 4294967295) ^ 2147483648) - 2147483648), ny, (((tw & 4294967295) ^ 2147483648) - 2147483648), nh);
}

function ui_scroll_step(scroll_pos: number, velocity: number, drag_delta: number, max_scroll: number, bounce_ios: number): number {
    let raw_vel: number = ((((((((velocity * 3) == -9223372036854775808) && (4 == -1)) ? -9223372036854775808 : Math.trunc((velocity * 3) / 4)) + drag_delta) & 4294967295) ^ 2147483648) - 2147483648);
    let raw_pos: number = ((((scroll_pos + raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
    if ((bounce_ios == 0)) {
        let clamped_pos: number = ui_constrain_dim(raw_pos, 0, max_scroll);
        let hit_edge: number = ((((((raw_pos < 0) || (raw_pos > max_scroll)) ? 1 : 0) & 4294967295) ^ 2147483648) - 2147483648);
        let clamped_vel: number = (((((hit_edge == 1) ? 0 : raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
        return ui_pack_rect(clamped_pos, clamped_vel, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    }
    let over_top: number = (((((raw_pos < 0) ? raw_pos : 0) & 4294967295) ^ 2147483648) - 2147483648);
    let over_bot: number = (((((raw_pos > max_scroll) ? (raw_pos - max_scroll) : 0) & 4294967295) ^ 2147483648) - 2147483648);
    let overscroll: number = ((((over_top + over_bot) & 4294967295) ^ 2147483648) - 2147483648);
    let spring_pull: number = ((((((overscroll == -9223372036854775808) && (3 == -1)) ? -9223372036854775808 : Math.trunc(overscroll / 3)) & 4294967295) ^ 2147483648) - 2147483648);
    let bounced_pos: number = ((((raw_pos - spring_pull) & 4294967295) ^ 2147483648) - 2147483648);
    let bounced_vel: number = (((((overscroll != 0) ? Math.trunc((raw_vel - spring_pull) / 2) : raw_vel) & 4294967295) ^ 2147483648) - 2147483648);
    return ui_pack_rect(bounced_pos, bounced_vel, overscroll, (((0 & 4294967295) ^ 2147483648) - 2147483648));
}

function ui_visible_card_index(scroll_pos: number, card_h: number, card_gap: number, total_cards: number): number {
    let stride: number = ((((card_h + card_gap) & 4294967295) ^ 2147483648) - 2147483648);
    let clamped_scroll: number = (((((scroll_pos < 0) ? 0 : scroll_pos) & 4294967295) ^ 2147483648) - 2147483648);
    let raw_idx: number = ((((((clamped_scroll == -9223372036854775808) && (stride == -1)) ? -9223372036854775808 : Math.trunc(clamped_scroll / stride)) & 4294967295) ^ 2147483648) - 2147483648);
    return (((ui_constrain_dim(raw_idx, 0, (total_cards - 1)) & 4294967295) ^ 2147483648) - 2147483648);
}

function ui_layout_list_card(body_rect: number, scroll_pos: number, card_h: number, card_gap: number, card_idx: number): number {
    let inner_body: number = ui_inset_rect(body_rect, (((12 & 4294967295) ^ 2147483648) - 2147483648), (((8 & 4294967295) ^ 2147483648) - 2147483648));
    let bx: number = ui_rect_lane(inner_body, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let by: number = ui_rect_lane(inner_body, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let bw: number = ui_rect_lane(inner_body, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let card_y: number = (((((by + (card_idx * (card_h + card_gap))) - scroll_pos) & 4294967295) ^ 2147483648) - 2147483648);
    let raw_card: number = ui_pack_rect(bx, card_y, bw, card_h);
    return ui_intersect_rect(raw_card, body_rect);
}

function ui_hit_test_nav(nav_rect: number, gap: number, px: number, py: number): number {
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

function ui_dispatch_event(state: number, viewport_rect: number, ev_type: number, px: number, py: number, delta_y: number, bounce_ios: number): number {
    let active_tab: number = ui_rect_lane(state, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let sel_card: number = ui_rect_lane(state, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let scroll_pos: number = ui_rect_lane(state, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let scroll_vel: number = ui_rect_lane(state, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    let safe_top: number = ((bounce_ios == 1) ? 48 : 24);
    let safe_bot: number = ((bounce_ios == 1) ? 34 : 16);
    let body_rect: number = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 1);
    let nav_rect: number = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 2);
    if ((ev_type == 1)) {
        let tapped_tab: number = ui_hit_test_nav(nav_rect, 8, px, py);
        if ((tapped_tab >= 0)) {
            return ui_pack_rect((((tapped_tab & 4294967295) ^ 2147483648) - 2147483648), sel_card, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
        }
        let vis_idx: number = ui_visible_card_index(scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), (((20 & 4294967295) ^ 2147483648) - 2147483648));
        let card_rect: number = ui_layout_list_card(body_rect, scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), vis_idx);
        let new_sel: number = ((ui_hit_test(card_rect, (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1) ? vis_idx : sel_card);
        return ui_pack_rect(active_tab, (((new_sel & 4294967295) ^ 2147483648) - 2147483648), scroll_pos, scroll_vel);
    }
    let step: number = ui_scroll_step(scroll_pos, scroll_vel, (((((ev_type == 2) ? delta_y : 0) & 4294967295) ^ 2147483648) - 2147483648), (((800 & 4294967295) ^ 2147483648) - 2147483648), (((bounce_ios & 4294967295) ^ 2147483648) - 2147483648));
    return ui_pack_rect(active_tab, sel_card, ui_rect_lane(step, (((0 & 4294967295) ^ 2147483648) - 2147483648)), ui_rect_lane(step, (((1 & 4294967295) ^ 2147483648) - 2147483648)));
}

function ui_simulate_mobile_session(vw: number, vh: number, bounce_ios: number, gesture_delta: number): number {
    let vp: number = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((vw & 4294967295) ^ 2147483648) - 2147483648), (((vh & 4294967295) ^ 2147483648) - 2147483648));
    let st: number = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((-1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    st = ui_dispatch_event(st, vp, 1, ((((vw ^ 2) < 0) && ((vw % 2) != 0)) ? (Math.trunc(vw / 2) - 1) : Math.trunc(vw / 2)), (vh - 40), 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 2, 0, 0, gesture_delta, bounce_ios);
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios);
    st = ui_dispatch_event(st, vp, 1, ((((vw ^ 2) < 0) && ((vw % 2) != 0)) ? (Math.trunc(vw / 2) - 1) : Math.trunc(vw / 2)), 140, 0, bounce_ios);
    let tab: number = ui_rect_lane(st, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let sel: number = ui_rect_lane(st, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let pos: number = ui_rect_lane(st, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let vel: number = ui_rect_lane(st, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    return ((((tab * 10000000) + (sel * 100000)) + (pos * 100)) + vel);
}
