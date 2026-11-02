// 02_dart_flexbox_solver.dart -- Flutter/Yoga-Style BoxConstraints, Flexbox & Scaffold Solver (Dart)

int ui_constrain_dim(int val, int min_v, int max_v) {
    int lo = (val < min_v ? min_v : val);
    return (lo > max_v ? max_v : lo);
}

int ui_align_offset(int container_len, int child_len, int align_mode) {
    int slack = (container_len > child_len ? (container_len - child_len) : 0);
    if (align_mode == 1) {
        return (slack ~/ 2);
    }
    if (align_mode == 2) {
        return slack;
    }
    return 0;
}

int ui_flex_child_size(int avail_main, int fixed_sum, int gap, int flex0, int flex1, int flex2, int child_idx) {
    int raw_free = avail_main - fixed_sum - (gap * 2);
    int free_space = (raw_free > 0 ? raw_free : 0);
    int total_flex = flex0 + flex1 + flex2;
    if (total_flex <= 0) {
        return 0;
    }
    int s0 = ((free_space * flex0) ~/ total_flex);
    int s1 = ((free_space * flex1) ~/ total_flex);
    int s2 = free_space - s0 - s1;
    return (child_idx == 0 ? s0 : (child_idx == 1 ? s1 : s2));
}

int ui_layout_scaffold_box(int viewport_rect, int safe_top, int safe_bottom, int appbar_h, int nav_h, int section_idx) {
    int vx = ui_rect_lane(viewport_rect, 0);
    int vy = ui_rect_lane(viewport_rect, 1);
    int vw = ui_rect_lane(viewport_rect, 2);
    int vh = ui_rect_lane(viewport_rect, 3);
    int inner_h = vh - safe_top - safe_bottom;
    int body_h = ui_flex_child_size(inner_h, appbar_h + nav_h, 0, 0, 1, 0, 1);
    if (section_idx == 0) {
        return ui_pack_rect(vx, vy + safe_top, vw, appbar_h);
    }
    if (section_idx == 1) {
        return ui_pack_rect(vx, vy + safe_top + appbar_h, vw, body_h);
    }
    return ui_pack_rect(vx, vy + safe_top + appbar_h + body_h, vw, nav_h);
}

int ui_layout_nav_tab(int nav_rect, int gap, int tab_idx) {
    int nx = ui_rect_lane(nav_rect, 0);
    int ny = ui_rect_lane(nav_rect, 1);
    int nw = ui_rect_lane(nav_rect, 2);
    int nh = ui_rect_lane(nav_rect, 3);
    int w0 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 0);
    int w1 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 1);
    int w2 = ui_flex_child_size(nw, 0, gap, 1, 1, 1, 2);
    int tx = (tab_idx == 0 ? nx : (tab_idx == 1 ? (nx + w0 + gap) : (nx + w0 + w1 + (gap * 2))));
    int tw = (tab_idx == 0 ? w0 : (tab_idx == 1 ? w1 : w2));
    return ui_pack_rect(tx, ny, tw, nh);
}
