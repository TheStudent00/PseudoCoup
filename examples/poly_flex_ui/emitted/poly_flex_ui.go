func ui_pack_rect(x int64, y int64, w int64, h int64) int64 {
    ux := (x & 65535)
    uy := ((y & 65535) << 16)
    uw := ((w & 65535) << 32)
    uh := ((h & 65535) << 48)
    return (((ux | uy) | uw) | uh)
}

func ui_rect_lane(rect int64, lane int64) int64 {
    shift := (((((lane & 3) * 16) & 4294967295) ^ 2147483648) - 2147483648)
    raw := ((rect >> (shift & 63)) & 65535)
    return (((((raw ^ 32768) - 32768) & 4294967295) ^ 2147483648) - 2147483648)
}

func ui_inset_rect(rect int64, pad_x int64, pad_y int64) int64 {
    x := ((((ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648)) + pad_x) & 4294967295) ^ 2147483648) - 2147483648)
    y := ((((ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648)) + pad_y) & 4294967295) ^ 2147483648) - 2147483648)
    w := ((((ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_x * 2)) & 4294967295) ^ 2147483648) - 2147483648)
    h := ((((ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648)) - (pad_y * 2)) & 4294967295) ^ 2147483648) - 2147483648)
    cw := (((func() int64 { if (w > 0) { return w } else { return 0 } }() & 4294967295) ^ 2147483648) - 2147483648)
    ch := (((func() int64 { if (h > 0) { return h } else { return 0 } }() & 4294967295) ^ 2147483648) - 2147483648)
    return ui_pack_rect(x, y, cw, ch)
}

func ui_hit_test(rect int64, px int64, py int64) int64 {
    x := ui_rect_lane(rect, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    y := ui_rect_lane(rect, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    w := ui_rect_lane(rect, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    h := ui_rect_lane(rect, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    if (((((px >= x) && (px < (x + w))) && (py >= y)) && (py < (y + h)))) {
        return (((1 & 4294967295) ^ 2147483648) - 2147483648)
    }
    return (((0 & 4294967295) ^ 2147483648) - 2147483648)
}

func ui_intersect_rect(a int64, b int64) int64 {
    ax0 := ui_rect_lane(a, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    ay0 := ui_rect_lane(a, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    ax1 := ((((ax0 + ui_rect_lane(a, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648)
    ay1 := ((((ay0 + ui_rect_lane(a, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648)
    bx0 := ui_rect_lane(b, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    by0 := ui_rect_lane(b, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    bx1 := ((((bx0 + ui_rect_lane(b, (((2 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648)
    by1 := ((((by0 + ui_rect_lane(b, (((3 & 4294967295) ^ 2147483648) - 2147483648))) & 4294967295) ^ 2147483648) - 2147483648)
    x0 := (((func() int64 { if (ax0 > bx0) { return ax0 } else { return bx0 } }() & 4294967295) ^ 2147483648) - 2147483648)
    y0 := (((func() int64 { if (ay0 > by0) { return ay0 } else { return by0 } }() & 4294967295) ^ 2147483648) - 2147483648)
    x1 := (((func() int64 { if (ax1 < bx1) { return ax1 } else { return bx1 } }() & 4294967295) ^ 2147483648) - 2147483648)
    y1 := (((func() int64 { if (ay1 < by1) { return ay1 } else { return by1 } }() & 4294967295) ^ 2147483648) - 2147483648)
    return ui_pack_rect(x0, y0, func() int64 { if (x1 > x0) { return (x1 - x0) } else { return 0 } }(), func() int64 { if (y1 > y0) { return (y1 - y0) } else { return 0 } }())
}

func ui_constrain_dim(val int64, min_v int64, max_v int64) int64 {
    lo := func() int64 { if (val < min_v) { return min_v } else { return val } }()
    return func() int64 { if (lo > max_v) { return max_v } else { return lo } }()
}

func ui_align_offset(container_len int64, child_len int64, align_mode int64) int64 {
    slack := func() int64 { if (container_len > child_len) { return (container_len - child_len) } else { return 0 } }()
    if ((align_mode == 1)) {
        return (slack / 2)
    }
    if ((align_mode == 2)) {
        return slack
    }
    return 0
}

func ui_flex_child_size(avail_main int64, fixed_sum int64, gap int64, flex0 int64, flex1 int64, flex2 int64, child_idx int64) int64 {
    raw_free := ((avail_main - fixed_sum) - (gap * 2))
    free_space := func() int64 { if (raw_free > 0) { return raw_free } else { return 0 } }()
    total_flex := ((flex0 + flex1) + flex2)
    if ((total_flex <= 0)) {
        return 0
    }
    s0 := ((free_space * flex0) / total_flex)
    s1 := ((free_space * flex1) / total_flex)
    s2 := ((free_space - s0) - s1)
    return func() int64 { if (child_idx == 0) { return s0 } else { return func() int64 { if (child_idx == 1) { return s1 } else { return s2 } }() } }()
}

func ui_layout_scaffold_box(viewport_rect int64, safe_top int64, safe_bottom int64, appbar_h int64, nav_h int64, section_idx int64) int64 {
    vx := ui_rect_lane(viewport_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    vy := ui_rect_lane(viewport_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    vw := ui_rect_lane(viewport_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    vh := ui_rect_lane(viewport_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    inner_h := ((vh - safe_top) - safe_bottom)
    body_h := ui_flex_child_size(inner_h, (appbar_h + nav_h), 0, 0, 1, 0, 1)
    if ((section_idx == 0)) {
        return ui_pack_rect(vx, ((((vy + safe_top) & 4294967295) ^ 2147483648) - 2147483648), vw, (((appbar_h & 4294967295) ^ 2147483648) - 2147483648))
    }
    if ((section_idx == 1)) {
        return ui_pack_rect(vx, (((((vy + safe_top) + appbar_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((body_h & 4294967295) ^ 2147483648) - 2147483648))
    }
    return ui_pack_rect(vx, ((((((vy + safe_top) + appbar_h) + body_h) & 4294967295) ^ 2147483648) - 2147483648), vw, (((nav_h & 4294967295) ^ 2147483648) - 2147483648))
}

func ui_layout_nav_tab(nav_rect int64, gap int64, tab_idx int64) int64 {
    nx := ui_rect_lane(nav_rect, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    ny := ui_rect_lane(nav_rect, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    nw := ui_rect_lane(nav_rect, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    nh := ui_rect_lane(nav_rect, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    w0 := ui_flex_child_size(nw, 0, gap, 1, 1, 1, 0)
    w1 := ui_flex_child_size(nw, 0, gap, 1, 1, 1, 1)
    w2 := ui_flex_child_size(nw, 0, gap, 1, 1, 1, 2)
    tx := func() int64 { if (tab_idx == 0) { return nx } else { return func() int64 { if (tab_idx == 1) { return ((nx + w0) + gap) } else { return (((nx + w0) + w1) + (gap * 2)) } }() } }()
    tw := func() int64 { if (tab_idx == 0) { return w0 } else { return func() int64 { if (tab_idx == 1) { return w1 } else { return w2 } }() } }()
    return ui_pack_rect((((tx & 4294967295) ^ 2147483648) - 2147483648), ny, (((tw & 4294967295) ^ 2147483648) - 2147483648), nh)
}

func ui_scroll_step(scroll_pos int64, velocity int64, drag_delta int64, max_scroll int64, bounce_ios int64) int64 {
    raw_vel := ((((((velocity * 3) / 4) + drag_delta) & 4294967295) ^ 2147483648) - 2147483648)
    raw_pos := ((((scroll_pos + raw_vel) & 4294967295) ^ 2147483648) - 2147483648)
    if ((bounce_ios == 0)) {
        clamped_pos := ui_constrain_dim(raw_pos, 0, max_scroll)
        hit_edge := (((func() int64 { if ((raw_pos < 0) || (raw_pos > max_scroll)) { return 1 } else { return 0 } }() & 4294967295) ^ 2147483648) - 2147483648)
        clamped_vel := (((func() int64 { if (hit_edge == 1) { return 0 } else { return raw_vel } }() & 4294967295) ^ 2147483648) - 2147483648)
        return ui_pack_rect(clamped_pos, clamped_vel, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648))
    }
    over_top := (((func() int64 { if (raw_pos < 0) { return raw_pos } else { return 0 } }() & 4294967295) ^ 2147483648) - 2147483648)
    over_bot := (((func() int64 { if (raw_pos > max_scroll) { return (raw_pos - max_scroll) } else { return 0 } }() & 4294967295) ^ 2147483648) - 2147483648)
    overscroll := ((((over_top + over_bot) & 4294967295) ^ 2147483648) - 2147483648)
    spring_pull := ((((overscroll / 3) & 4294967295) ^ 2147483648) - 2147483648)
    bounced_pos := ((((raw_pos - spring_pull) & 4294967295) ^ 2147483648) - 2147483648)
    bounced_vel := (((func() int64 { if (overscroll != 0) { return ((raw_vel - spring_pull) / 2) } else { return raw_vel } }() & 4294967295) ^ 2147483648) - 2147483648)
    return ui_pack_rect(bounced_pos, bounced_vel, overscroll, (((0 & 4294967295) ^ 2147483648) - 2147483648))
}

func ui_visible_card_index(scroll_pos int64, card_h int64, card_gap int64, total_cards int64) int64 {
    stride := ((((card_h + card_gap) & 4294967295) ^ 2147483648) - 2147483648)
    clamped_scroll := (((func() int64 { if (scroll_pos < 0) { return 0 } else { return scroll_pos } }() & 4294967295) ^ 2147483648) - 2147483648)
    raw_idx := ((((clamped_scroll / stride) & 4294967295) ^ 2147483648) - 2147483648)
    return (((ui_constrain_dim(raw_idx, 0, (total_cards - 1)) & 4294967295) ^ 2147483648) - 2147483648)
}

func ui_layout_list_card(body_rect int64, scroll_pos int64, card_h int64, card_gap int64, card_idx int64) int64 {
    inner_body := ui_inset_rect(body_rect, (((12 & 4294967295) ^ 2147483648) - 2147483648), (((8 & 4294967295) ^ 2147483648) - 2147483648))
    bx := ui_rect_lane(inner_body, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    by := ui_rect_lane(inner_body, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    bw := ui_rect_lane(inner_body, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    card_y := (((((by + (card_idx * (card_h + card_gap))) - scroll_pos) & 4294967295) ^ 2147483648) - 2147483648)
    raw_card := ui_pack_rect(bx, card_y, bw, card_h)
    return ui_intersect_rect(raw_card, body_rect)
}

func ui_hit_test_nav(nav_rect int64, gap int64, px int64, py int64) int64 {
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

func ui_dispatch_event(state int64, viewport_rect int64, ev_type int64, px int64, py int64, delta_y int64, bounce_ios int64) int64 {
    active_tab := ui_rect_lane(state, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    sel_card := ui_rect_lane(state, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    scroll_pos := ui_rect_lane(state, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    scroll_vel := ui_rect_lane(state, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    safe_top := func() int64 { if (bounce_ios == 1) { return 48 } else { return 24 } }()
    safe_bot := func() int64 { if (bounce_ios == 1) { return 34 } else { return 16 } }()
    body_rect := ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 1)
    nav_rect := ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 2)
    if ((ev_type == 1)) {
        tapped_tab := ui_hit_test_nav(nav_rect, 8, px, py)
        if ((tapped_tab >= 0)) {
            return ui_pack_rect((((tapped_tab & 4294967295) ^ 2147483648) - 2147483648), sel_card, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648))
        }
        vis_idx := ui_visible_card_index(scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), (((20 & 4294967295) ^ 2147483648) - 2147483648))
        card_rect := ui_layout_list_card(body_rect, scroll_pos, (((72 & 4294967295) ^ 2147483648) - 2147483648), (((10 & 4294967295) ^ 2147483648) - 2147483648), vis_idx)
        new_sel := func() int64 { if (ui_hit_test(card_rect, (((px & 4294967295) ^ 2147483648) - 2147483648), (((py & 4294967295) ^ 2147483648) - 2147483648)) == 1) { return vis_idx } else { return sel_card } }()
        return ui_pack_rect(active_tab, (((new_sel & 4294967295) ^ 2147483648) - 2147483648), scroll_pos, scroll_vel)
    }
    step := ui_scroll_step(scroll_pos, scroll_vel, (((func() int64 { if (ev_type == 2) { return delta_y } else { return 0 } }() & 4294967295) ^ 2147483648) - 2147483648), (((800 & 4294967295) ^ 2147483648) - 2147483648), (((bounce_ios & 4294967295) ^ 2147483648) - 2147483648))
    return ui_pack_rect(active_tab, sel_card, ui_rect_lane(step, (((0 & 4294967295) ^ 2147483648) - 2147483648)), ui_rect_lane(step, (((1 & 4294967295) ^ 2147483648) - 2147483648)))
}

func ui_simulate_mobile_session(vw int64, vh int64, bounce_ios int64, gesture_delta int64) int64 {
    vp := ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((vw & 4294967295) ^ 2147483648) - 2147483648), (((vh & 4294967295) ^ 2147483648) - 2147483648))
    st := ui_pack_rect((((0 & 4294967295) ^ 2147483648) - 2147483648), (((-1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648))
    st = ui_dispatch_event(st, vp, 1, func() int64 { if (((vw ^ 2) < 0) && ((vw % 2) != 0)) { return ((vw / 2) - 1) } else { return (vw / 2) } }(), (vh - 40), 0, bounce_ios)
    st = ui_dispatch_event(st, vp, 2, 0, 0, gesture_delta, bounce_ios)
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios)
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios)
    st = ui_dispatch_event(st, vp, 1, func() int64 { if (((vw ^ 2) < 0) && ((vw % 2) != 0)) { return ((vw / 2) - 1) } else { return (vw / 2) } }(), 140, 0, bounce_ios)
    tab := ui_rect_lane(st, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    sel := ui_rect_lane(st, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    pos := ui_rect_lane(st, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    vel := ui_rect_lane(st, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    return ((((tab * 10000000) + (sel * 100000)) + (pos * 100)) + vel)
}
