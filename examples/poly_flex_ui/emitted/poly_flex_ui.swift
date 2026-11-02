func ui_pack_rect(_ x: Int64, _ y: Int64, _ w: Int64, _ h: Int64) -> Int64 {
    var ux: Int64 = (x & 65535)
    var uy: Int64 = ((y & 65535) << (16 & 63))
    var uw: Int64 = ((w & 65535) << (32 & 63))
    var uh: Int64 = ((h & 65535) << (48 & 63))
    return (((ux | uy) | uw) | uh)
}

func ui_rect_lane(_ rect: Int64, _ lane: Int64) -> Int64 {
    var shift: Int64 = (((((lane & 3) * 16) & 4294967295) ^ 2147483648) - 2147483648)
    var raw: Int64 = ((rect >> (shift & 63)) & 65535)
    return (((((raw ^ 32768) - 32768) & 4294967295) ^ 2147483648) - 2147483648)
}

func ui_inset_rect(_ rect: Int64, _ pad_x: Int64, _ pad_y: Int64) -> Int64 {
    var x: Int64 = ((((ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648)) + pad_x) & 4294967295) ^ 2147483648) - 2147483648)
    var y: Int64 = ((((ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648)) + pad_y) & 4294967295) ^ 2147483648) - 2147483648)
    var w: Int64 = ((((ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_x * 2)) & 4294967295) ^ 2147483648) - 2147483648)
    var h: Int64 = ((((ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_y * 2)) & 4294967295) ^ 2147483648) - 2147483648)
    var cw: Int64 = (((((w > 0) ? w : 0) & 4294967295) ^ 2147483648) - 2147483648)
    var ch: Int64 = (((((h > 0) ? h : 0) & 4294967295) ^ 2147483648) - 2147483648)
    return ui_pack_rect(x, y, cw, ch)
}

func ui_hit_test(_ rect: Int64, _ px: Int64, _ py: Int64) -> Int64 {
    var x: Int64 = ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    var y: Int64 = ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    var w: Int64 = ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    var h: Int64 = ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    if (((((px >= x) && (px < (x + w))) && (py >= y)) && (py < (y + h)))) {
        return (((1 & 4294967295) ^ 2147483648) - 2147483648)
    }
    return (((0 & 4294967295) ^ 2147483648) - 2147483648)
}

func ui_intersect_rect(_ a: Int64, _ b: Int64) -> Int64 {
    var ax0: Int64 = ui_rect_lane(a, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    var ay0: Int64 = ui_rect_lane(a, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    var ax1: Int64 = ((((ax0 + ui_rect_lane(a, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648)
    var ay1: Int64 = ((((ay0 + ui_rect_lane(a, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648)
    var bx0: Int64 = ui_rect_lane(b, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    var by0: Int64 = ui_rect_lane(b, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    var bx1: Int64 = ((((bx0 + ui_rect_lane(b, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648)
    var by1: Int64 = ((((by0 + ui_rect_lane(b, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648)
    var x0: Int64 = (((((ax0 > bx0) ? ax0 : bx0) & 4294967295) ^ 2147483648) - 2147483648)
    var y0: Int64 = (((((ay0 > by0) ? ay0 : by0) & 4294967295) ^ 2147483648) - 2147483648)
    var x1: Int64 = (((((ax1 < bx1) ? ax1 : bx1) & 4294967295) ^ 2147483648) - 2147483648)
    var y1: Int64 = (((((ay1 < by1) ? ay1 : by1) & 4294967295) ^ 2147483648) - 2147483648)
    return ui_pack_rect(x0, y0, ((x1 > x0) ? (x1 - x0) : 0), ((y1 > y0) ? (y1 - y0) : 0))
}

func ui_constrain_dim(_ val: Int64, _ min_v: Int64, _ max_v: Int64) -> Int64 {
    var lo: Int64 = ((val < min_v) ? min_v : val)
    return ((lo > max_v) ? max_v : lo)
}

func ui_align_offset(_ container_len: Int64, _ child_len: Int64, _ align_mode: Int64) -> Int64 {
    var slack: Int64 = ((container_len > child_len) ? (container_len - child_len) : 0)
    if ((align_mode == 1)) {
        return (slack / 2)
    }
    if ((align_mode == 2)) {
        return slack
    }
    return 0
}

func ui_flex_child_size(_ avail_main: Int64, _ fixed_sum: Int64, _ gap: Int64, _ flex0: Int64, _ flex1: Int64, _ flex2: Int64, _ child_idx: Int64) -> Int64 {
    var raw_free: Int64 = ((avail_main - fixed_sum) - (gap * 2))
    var free_space: Int64 = ((raw_free > 0) ? raw_free : 0)
    var total_flex: Int64 = ((flex0 + flex1) + flex2)
    if ((total_flex <= 0)) {
        return 0
    }
    var s0: Int64 = ((((free_space * flex0) == -9223372036854775808) && (total_flex == -1)) ? -9223372036854775808 : ((free_space * flex0) / total_flex))
    var s1: Int64 = ((((free_space * flex1) == -9223372036854775808) && (total_flex == -1)) ? -9223372036854775808 : ((free_space * flex1) / total_flex))
    var s2: Int64 = ((free_space - s0) - s1)
    return ((child_idx == 0) ? s0 : ((child_idx == 1) ? s1 : s2))
}

func ui_layout_scaffold_box(_ viewport_rect: Int64, _ safe_top: Int64, _ safe_bottom: Int64, _ appbar_h: Int64, _ nav_h: Int64, _ section_idx: Int64) -> Int64 {
    var vx: Int64 = ui_rect_lane(viewport_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    var vy: Int64 = ui_rect_lane(viewport_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    var vw: Int64 = ui_rect_lane(viewport_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    var vh: Int64 = ui_rect_lane(viewport_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    var inner_h: Int64 = ((vh - safe_top) - safe_bottom)
    var body_h: Int64 = ui_flex_child_size(inner_h, (appbar_h + nav_h), 0, 0, 1, 0, 1)
    if ((section_idx == 0)) {
        return ui_pack_rect(vx, ((((vy + safe_top) & 4294967295) ^ 2147483648) - 2147483648), vw, (((appbar_h & 4294967295) ^ 2147483648) - 2147483648))
    }
    if ((section_idx == 1)) {
        return ui_pack_rect(vx, (((((vy + safe_top) + appbar_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((body_h & 4294967295) ^ 2147483648) - 2147483648))
    }
    return ui_pack_rect(vx, ((((((vy + safe_top) + appbar_h) + body_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((nav_h & 4294967295) ^ 2147483648) - 2147483648))
}

func ui_layout_nav_tab(_ nav_rect: Int64, _ gap: Int64, _ tab_idx: Int64) -> Int64 {
    var nx: Int64 = ui_rect_lane(nav_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    var ny: Int64 = ui_rect_lane(nav_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    var nw: Int64 = ui_rect_lane(nav_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    var nh: Int64 = ui_rect_lane(nav_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    var w0: Int64 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 0)
    var w1: Int64 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 1)
    var w2: Int64 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 2)
    var tx: Int64 = ((tab_idx == 0) ? nx : ((tab_idx == 1) ? ((nx + w0) + gap) : (((nx + w0) + w1) + (gap * 2))))
    var tw: Int64 = ((tab_idx == 0) ? w0 : ((tab_idx == 1) ? w1 : w2))
    return ui_pack_rect((((tx & 4294967295) ^ 2147483648) - 2147483648), ny, (((tw & 4294967295) ^ 2147483648) - 2147483648), nh)
}

func ui_scroll_step(_ scroll_pos: Int64, _ velocity: Int64, _ drag_delta: Int64, _ max_scroll: Int64, _ bounce_ios: Int64) -> Int64 {
    var raw_vel: Int64 = ((((((((velocity * 3) == -9223372036854775808) && (4 == -1)) ? -9223372036854775808 : ((velocity * 3) / 4)) + drag_delta) & 4294967295) ^ 2147483648) - 2147483648)
    var raw_pos: Int64 = ((((scroll_pos + raw_vel) & 4294967295) ^ 2147483648) - 2147483648)
    if ((bounce_ios == 0)) {
        var clamped_pos: Int64 = ui_constrain_dim(raw_pos, 0, max_scroll)
        var hit_edge: Int64 = ((((((raw_pos < 0) || (raw_pos > max_scroll)) ? 1 : 0) & 4294967295) ^ 2147483648) - 2147483648)
        var clamped_vel: Int64 = (((((hit_edge == 1) ? 0 : raw_vel) & 4294967295) ^ 2147483648) - 2147483648)
        return ui_pack_rect(clamped_pos, clamped_vel, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648))
    }
    var over_top: Int64 = (((((raw_pos < 0) ? raw_pos : 0) & 4294967295) ^ 2147483648) - 2147483648)
    var over_bot: Int64 = (((((raw_pos > max_scroll) ? (raw_pos - max_scroll) : 0) & 4294967295) ^ 2147483648) - 2147483648)
    var overscroll: Int64 = ((((over_top + over_bot) & 4294967295) ^ 2147483648) - 2147483648)
    var spring_pull: Int64 = ((((((overscroll == -9223372036854775808) && (3 == -1)) ? -9223372036854775808 : (overscroll / 3)) & 4294967295) ^ 2147483648) - 2147483648)
    var bounced_pos: Int64 = ((((raw_pos - spring_pull) & 4294967295) ^ 2147483648) - 2147483648)
    var bounced_vel: Int64 = (((((overscroll != 0) ? ((raw_vel - spring_pull) / 2) : raw_vel) & 4294967295) ^ 2147483648) - 2147483648)
    return ui_pack_rect(bounced_pos, bounced_vel, overscroll, (((0 & 4294967295) ^ 2147483648) - 2147483648))
}

func ui_visible_card_index(_ scroll_pos: Int64, _ card_h: Int64, _ card_gap: Int64, _ total_cards: Int64) -> Int64 {
    var stride: Int64 = ((((card_h + card_gap) & 4294967295) ^ 2147483648) - 2147483648)
    var clamped_scroll: Int64 = (((((scroll_pos < 0) ? 0 : scroll_pos) & 4294967295) ^ 2147483648) - 2147483648)
    var raw_idx: Int64 = ((((((clamped_scroll == -9223372036854775808) && (stride == -1)) ? -9223372036854775808 : (clamped_scroll / stride)) & 4294967295) ^ 2147483648) - 2147483648)
    return (((ui_constrain_dim(raw_idx, 0, (total_cards - 1)) & 4294967295) ^ 2147483648) - 2147483648)
}

func ui_layout_list_card(_ body_rect: Int64, _ scroll_pos: Int64, _ card_h: Int64, _ card_gap: Int64, _ card_idx: Int64) -> Int64 {
    var inner_body: Int64 = ui_inset_rect(body_rect, (((12 & 4294967295) ^ 2147483648) - 2147483648), (((8 & 4294967295) ^ 2147483648) - 2147483648))
    var bx: Int64 = ui_rect_lane(inner_body, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    var by: Int64 = ui_rect_lane(inner_body, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    var bw: Int64 = ui_rect_lane(inner_body, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    var card_y: Int64 = (((((by + (card_idx * (card_h + card_gap))) - scroll_pos) & 4294967295) ^ 2147483648) - 2147483648)
    var raw_card: Int64 = ui_pack_rect(bx, card_y, bw, card_h)
    return ui_intersect_rect(raw_card, body_rect)
}

func ui_hit_test_nav(_ nav_rect: Int64, _ gap: Int64, _ px: Int64, _ py: Int64) -> Int64 {
    if ((ui_hit_test(ui_layout_nav_tab(nav_rect, gap, 0), (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1)) {
        return 0
    }
    if ((ui_hit_test(ui_layout_nav_tab(nav_rect, gap, 1), (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1)) {
        return 1
    }
    if ((ui_hit_test(ui_layout_nav_tab(nav_rect, gap, 2), (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1)) {
        return 2
    }
    return -1
}

func ui_dispatch_event(_ state: Int64, _ viewport_rect: Int64, _ ev_type: Int64, _ px: Int64, _ py: Int64, _ delta_y: Int64, _ bounce_ios: Int64) -> Int64 {
    var active_tab: Int64 = ui_rect_lane(state, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    var sel_card: Int64 = ui_rect_lane(state, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    var scroll_pos: Int64 = ui_rect_lane(state, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    var scroll_vel: Int64 = ui_rect_lane(state, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    var safe_top: Int64 = ((bounce_ios == 1) ? 48 : 24)
    var safe_bot: Int64 = ((bounce_ios == 1) ? 34 : 16)
    var body_rect: Int64 = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 1)
    var nav_rect: Int64 = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 2)
    if ((ev_type == 1)) {
        var tapped_tab: Int64 = ui_hit_test_nav(nav_rect, 8, px, py)
        if ((tapped_tab >= 0)) {
            return ui_pack_rect((((tapped_tab & 4294967295) ^ 2147483648) - 2147483648), sel_card, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648))
        }
        var vis_idx: Int64 = ui_visible_card_index(scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), (((20 & 4294967295) ^ 2147483648) - 2147483648))
        var card_rect: Int64 = ui_layout_list_card(body_rect, scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), vis_idx)
        var new_sel: Int64 = ((ui_hit_test(card_rect, (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1) ? vis_idx : sel_card)
        return ui_pack_rect(active_tab, (((new_sel & 4294967295) ^ 2147483648) - 2147483648), scroll_pos, scroll_vel)
    }
    var step: Int64 = ui_scroll_step(scroll_pos, scroll_vel, (((((ev_type == 2) ? delta_y : 0) & 4294967295) ^ 2147483648) - 2147483648), (((800 & 4294967295) ^ 2147483648) - 2147483648), (((bounce_ios & 4294967295) ^ 2147483648) - 2147483648))
    return ui_pack_rect(active_tab, sel_card, ui_rect_lane(step, (((0 & 4294967295) ^ 2147483648) - 2147483648)), ui_rect_lane(step, (((1 & 4294967295) ^ 2147483648) - 2147483648)))
}

func ui_simulate_mobile_session(_ vw: Int64, _ vh: Int64, _ bounce_ios: Int64, _ gesture_delta: Int64) -> Int64 {
    var vp: Int64 = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((vw & 4294967295) ^ 2147483648) - 2147483648), (((vh & 4294967295) ^ 2147483648) - 2147483648))
    var st: Int64 = ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((-1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648))
    st = ui_dispatch_event(st, vp, 1, ((((vw ^ 2) < 0) && ((vw % 2) != 0)) ? ((vw / 2) - 1) : (vw / 2)), (vh - 40), 0, bounce_ios)
    st = ui_dispatch_event(st, vp, 2, 0, 0, gesture_delta, bounce_ios)
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios)
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios)
    st = ui_dispatch_event(st, vp, 1, ((((vw ^ 2) < 0) && ((vw % 2) != 0)) ? ((vw / 2) - 1) : (vw / 2)), 140, 0, bounce_ios)
    var tab: Int64 = ui_rect_lane(st, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    var sel: Int64 = ui_rect_lane(st, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    var pos: Int64 = ui_rect_lane(st, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    var vel: Int64 = ui_rect_lane(st, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    return ((((tab * 10000000) + (sel * 100000)) + (pos * 100)) + vel)
}
