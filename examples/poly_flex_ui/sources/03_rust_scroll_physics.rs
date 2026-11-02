// 03_rust_scroll_physics.rs -- iOS Bouncing vs Android Clamping Scroll Physics & Virtual ListView (Rust)

fn ui_scroll_step(scroll_pos: i32, velocity: i32, drag_delta: i32, max_scroll: i32, bounce_ios: i32) -> i64 {
    let raw_vel: i32 = ((velocity * 3) / 4) + drag_delta;
    let raw_pos: i32 = scroll_pos + raw_vel;
    if bounce_ios == 0 {
        let clamped_pos: i32 = ui_constrain_dim(raw_pos, 0, max_scroll);
        let hit_edge: i32 = (if raw_pos < 0 || raw_pos > max_scroll { 1 } else { 0 });
        let clamped_vel: i32 = (if hit_edge == 1 { 0 } else { raw_vel });
        return ui_pack_rect(clamped_pos, clamped_vel, 0, 0);
    }
    let over_top: i32 = (if raw_pos < 0 { raw_pos } else { 0 });
    let over_bot: i32 = (if raw_pos > max_scroll { (raw_pos - max_scroll) } else { 0 });
    let overscroll: i32 = over_top + over_bot;
    let spring_pull: i32 = overscroll / 3;
    let bounced_pos: i32 = raw_pos - spring_pull;
    let bounced_vel: i32 = (if overscroll != 0 { ((raw_vel - spring_pull) / 2) } else { raw_vel });
    return ui_pack_rect(bounced_pos, bounced_vel, overscroll, 0);
}

fn ui_visible_card_index(scroll_pos: i32, card_h: i32, card_gap: i32, total_cards: i32) -> i32 {
    let stride: i32 = card_h + card_gap;
    let clamped_scroll: i32 = (if scroll_pos < 0 { 0 } else { scroll_pos });
    let raw_idx: i32 = clamped_scroll / stride;
    return ui_constrain_dim(raw_idx, 0, total_cards - 1);
}

fn ui_layout_list_card(body_rect: i64, scroll_pos: i32, card_h: i32, card_gap: i32, card_idx: i32) -> i64 {
    let inner_body: i64 = ui_inset_rect(body_rect, 12, 8);
    let bx: i32 = ui_rect_lane(inner_body, 0);
    let by: i32 = ui_rect_lane(inner_body, 1);
    let bw: i32 = ui_rect_lane(inner_body, 2);
    let card_y: i32 = by + (card_idx * (card_h + card_gap)) - scroll_pos;
    let raw_card: i64 = ui_pack_rect(bx, card_y, bw, card_h);
    return ui_intersect_rect(raw_card, body_rect);
}
