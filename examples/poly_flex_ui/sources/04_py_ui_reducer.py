# 04_py_ui_reducer.py -- Reactive UI Event Reducer & Laptop-to-Mobile Session Harness (Python)

def ui_hit_test_nav(nav_rect: int, gap: int, px: int, py: int) -> int:
    if ui_hit_test(ui_layout_nav_tab(nav_rect, gap, 0), px, py) == 1:
        return 0
    if ui_hit_test(ui_layout_nav_tab(nav_rect, gap, 1), px, py) == 1:
        return 1
    if ui_hit_test(ui_layout_nav_tab(nav_rect, gap, 2), px, py) == 1:
        return 2
    return -1

def ui_dispatch_event(state: int, viewport_rect: int, ev_type: int, px: int, py: int, delta_y: int, bounce_ios: int) -> int:
    active_tab = ui_rect_lane(state, 0)
    sel_card = ui_rect_lane(state, 1)
    scroll_pos = ui_rect_lane(state, 2)
    scroll_vel = ui_rect_lane(state, 3)
    safe_top = (48 if bounce_ios == 1 else 24)
    safe_bot = (34 if bounce_ios == 1 else 16)
    body_rect = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 1)
    nav_rect = ui_layout_scaffold_box(viewport_rect, safe_top, safe_bot, 56, 64, 2)
    if ev_type == 1:
        tapped_tab = ui_hit_test_nav(nav_rect, 8, px, py)
        if tapped_tab >= 0:
            return ui_pack_rect(tapped_tab, sel_card, 0, 0)
        vis_idx = ui_visible_card_index(scroll_pos, 72, 10, 20)
        card_rect = ui_layout_list_card(body_rect, scroll_pos, 72, 10, vis_idx)
        new_sel = (vis_idx if ui_hit_test(card_rect, px, py) == 1 else sel_card)
        return ui_pack_rect(active_tab, new_sel, scroll_pos, scroll_vel)
    step = ui_scroll_step(scroll_pos, scroll_vel, (delta_y if ev_type == 2 else 0), 800, bounce_ios)
    return ui_pack_rect(active_tab, sel_card, ui_rect_lane(step, 0), ui_rect_lane(step, 1))

def ui_simulate_mobile_session(vw: int, vh: int, bounce_ios: int, gesture_delta: int) -> int:
    vp = ui_pack_rect(0, 0, vw, vh)
    st = ui_pack_rect(0, -1, 0, 0)
    st = ui_dispatch_event(st, vp, 1, vw // 2, vh - 40, 0, bounce_ios)
    st = ui_dispatch_event(st, vp, 2, 0, 0, gesture_delta, bounce_ios)
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios)
    st = ui_dispatch_event(st, vp, 3, 0, 0, 0, bounce_ios)
    st = ui_dispatch_event(st, vp, 1, vw // 2, 140, 0, bounce_ios)
    tab = ui_rect_lane(st, 0)
    sel = ui_rect_lane(st, 1)
    pos = ui_rect_lane(st, 2)
    vel = ui_rect_lane(st, 3)
    return (tab * 10000000) + (sel * 100000) + (pos * 100) + vel
