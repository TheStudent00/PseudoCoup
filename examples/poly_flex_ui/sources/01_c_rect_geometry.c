// 01_c_rect_geometry.c -- 2D UI Bounding Box (`Rect64`), Safe-Area Insets & Hit-Testing (C)
// Packs (x, y, w, h) as 4x signed 16-bit lanes into a single 64-bit integer.

int64_t ui_pack_rect(int32_t x, int32_t y, int32_t w, int32_t h) {
    int64_t ux = x & 65535;
    int64_t uy = (y & 65535) << 16;
    int64_t uw = (w & 65535) << 32;
    int64_t uh = (h & 65535) << 48;
    return ux | uy | uw | uh;
}

int32_t ui_rect_lane(int64_t rect, int32_t lane) {
    int32_t shift = (lane & 3) * 16;
    int64_t raw = (rect >> shift) & 65535;
    return (raw ^ 32768) - 32768;
}

int64_t ui_inset_rect(int64_t rect, int32_t pad_x, int32_t pad_y) {
    int32_t x = ui_rect_lane(rect, 0) + pad_x;
    int32_t y = ui_rect_lane(rect, 1) + pad_y;
    int32_t w = ui_rect_lane(rect, 2) - (pad_x * 2);
    int32_t h = ui_rect_lane(rect, 3) - (pad_y * 2);
    int32_t cw = (w > 0 ? w : 0);
    int32_t ch = (h > 0 ? h : 0);
    return ui_pack_rect(x, y, cw, ch);
}

int32_t ui_hit_test(int64_t rect, int32_t px, int32_t py) {
    int32_t x = ui_rect_lane(rect, 0);
    int32_t y = ui_rect_lane(rect, 1);
    int32_t w = ui_rect_lane(rect, 2);
    int32_t h = ui_rect_lane(rect, 3);
    if (px >= x && px < (x + w) && py >= y && py < (y + h)) {
        return 1;
    }
    return 0;
}

int64_t ui_intersect_rect(int64_t a, int64_t b) {
    int32_t ax0 = ui_rect_lane(a, 0);
    int32_t ay0 = ui_rect_lane(a, 1);
    int32_t ax1 = ax0 + ui_rect_lane(a, 2);
    int32_t ay1 = ay0 + ui_rect_lane(a, 3);
    int32_t bx0 = ui_rect_lane(b, 0);
    int32_t by0 = ui_rect_lane(b, 1);
    int32_t bx1 = bx0 + ui_rect_lane(b, 2);
    int32_t by1 = by0 + ui_rect_lane(b, 3);
    int32_t x0 = (ax0 > bx0 ? ax0 : bx0);
    int32_t y0 = (ay0 > by0 ? ay0 : by0);
    int32_t x1 = (ax1 < bx1 ? ax1 : bx1);
    int32_t y1 = (ay1 < by1 ? ay1 : by1);
    return ui_pack_rect(x0, y0, (x1 > x0 ? (x1 - x0) : 0), (y1 > y0 ? (y1 - y0) : 0));
}
