// Three-Body Screensaver — native macOS .saver bundle
// Reads config from config.toml in the bundle Resources.

#import <ScreenSaver/ScreenSaver.h>
#include <math.h>
#include <stdlib.h>

#define MAX_STARS 10
#define MAX_TAIL 2000

typedef struct {
    double mass, radius;
    double x, y, vx, vy;
    double tail_x[MAX_TAIL], tail_y[MAX_TAIL];
    int tail_len, tail_start, tail_count;
    double cr, cg, cb;
} Star;

typedef struct {
    double G, dt;
    int steps_per_frame;
    int fps, tail_length;
    double star_scale, star_min, star_max;
    double bg_r, bg_g, bg_b;
    double zoom_margin, damping, min_scale, max_scale;
    Star stars[MAX_STARS];
    int num_stars;
    double smooth_scale, smooth_ox, smooth_oy;
} Sim;

static void tail_push(Star *s, double x, double y) {
    int idx = (s->tail_start + s->tail_count) % s->tail_len;
    s->tail_x[idx] = x;
    s->tail_y[idx] = y;
    if (s->tail_count < s->tail_len)
        s->tail_count++;
    else
        s->tail_start = (s->tail_start + 1) % s->tail_len;
}

static void sim_step(Sim *sim) {
    int n = sim->num_stars;
    double ax[MAX_STARS] = {0}, ay[MAX_STARS] = {0};
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (i == j) continue;
            double dx = sim->stars[i].x - sim->stars[j].x;
            double dy = sim->stars[i].y - sim->stars[j].y;
            double r = sqrt(dx*dx + dy*dy);
            if (r < 0.01) continue;
            double f = sim->G * sim->stars[j].mass / r;
            ax[i] -= (dx/r) * f;
            ay[i] -= (dy/r) * f;
        }
    }
    for (int i = 0; i < n; i++) {
        double hx = 0.5 * sim->dt * ax[i];
        double hy = 0.5 * sim->dt * ay[i];
        sim->stars[i].vx += hx;
        sim->stars[i].vy += hy;
        sim->stars[i].x += sim->stars[i].vx * sim->dt;
        sim->stars[i].y += sim->stars[i].vy * sim->dt;
        sim->stars[i].vx += hx;
        sim->stars[i].vy += hy;
        tail_push(&sim->stars[i],
                  sim->stars[i].x, sim->stars[i].y);
    }
}

static void center_frame(Sim *sim) {
    double tm = 0, px = 0, py = 0, cx = 0, cy = 0;
    for (int i = 0; i < sim->num_stars; i++) {
        tm += sim->stars[i].mass;
        px += sim->stars[i].mass * sim->stars[i].vx;
        py += sim->stars[i].mass * sim->stars[i].vy;
        cx += sim->stars[i].mass * sim->stars[i].x;
        cy += sim->stars[i].mass * sim->stars[i].y;
    }
    cx /= tm; cy /= tm;
    for (int i = 0; i < sim->num_stars; i++) {
        sim->stars[i].vx -= px / tm;
        sim->stars[i].vy -= py / tm;
        sim->stars[i].x -= cx;
        sim->stars[i].y -= cy;
        sim->stars[i].tail_start = 0;
        sim->stars[i].tail_count = 0;
        tail_push(&sim->stars[i],
                  sim->stars[i].x, sim->stars[i].y);
    }
}

static void parse_hex(const char *hex, double *r,
                      double *g, double *b) {
    unsigned int rv = 0, gv = 0, bv = 0;
    if (hex[0] == '#') hex++;
    sscanf(hex, "%02x%02x%02x", &rv, &gv, &bv);
    *r = rv / 255.0; *g = gv / 255.0; *b = bv / 255.0;
}

// Simple TOML parser — just enough for our config format
static Sim *load_config(NSString *path) {
    Sim *sim = calloc(1, sizeof(Sim));
    // Defaults
    sim->G = 0.667430; sim->dt = 0.03;
    sim->steps_per_frame = 1; sim->fps = 60;
    sim->tail_length = 600;
    sim->star_scale = 0.15; sim->star_min = 3;
    sim->star_max = 30;
    sim->bg_r = 0; sim->bg_g = 0; sim->bg_b = 0;
    sim->zoom_margin = 1.3; sim->damping = 0.03;
    sim->min_scale = 1.0; sim->max_scale = 50.0;

    NSString *content = [NSString stringWithContentsOfFile:path
        encoding:NSUTF8StringEncoding error:nil];
    if (!content) return sim;

    int cur_star = -1;
    for (NSString *raw in [content componentsSeparatedByString:@"\n"]) {
        NSString *line = [raw stringByTrimmingCharactersInSet:
            [NSCharacterSet whitespaceCharacterSet]];
        if ([line hasPrefix:@"#"] || [line length] == 0) continue;

        if ([line isEqualToString:@"[[stars]]"]) {
            cur_star = sim->num_stars++;
            sim->stars[cur_star].tail_len =
                sim->tail_length < MAX_TAIL ?
                sim->tail_length : MAX_TAIL;
            continue;
        }

        NSRange eq = [line rangeOfString:@"="];
        if (eq.location == NSNotFound) continue;
        NSString *key = [[line substringToIndex:eq.location]
            stringByTrimmingCharactersInSet:
            [NSCharacterSet whitespaceCharacterSet]];
        NSString *val = [[line substringFromIndex:
            eq.location + eq.length]
            stringByTrimmingCharactersInSet:
            [NSCharacterSet whitespaceCharacterSet]];
        // Strip inline comments
        NSRange cmt = [val rangeOfString:@"#"];
        if (cmt.location != NSNotFound)
            val = [[val substringToIndex:cmt.location]
                stringByTrimmingCharactersInSet:
                [NSCharacterSet whitespaceCharacterSet]];

        double dv = [val doubleValue];

        // Physics
        if ([key isEqualToString:@"G"]) sim->G = dv;
        else if ([key isEqualToString:@"dt"]) sim->dt = dv;
        else if ([key isEqualToString:@"steps_per_frame"])
            sim->steps_per_frame = (int)dv;
        // Display
        else if ([key isEqualToString:@"fps"])
            sim->fps = (int)dv;
        else if ([key isEqualToString:@"tail_length"])
            sim->tail_length = (int)dv < MAX_TAIL ?
                (int)dv : MAX_TAIL;
        else if ([key isEqualToString:@"star_scale"])
            sim->star_scale = dv;
        else if ([key isEqualToString:@"star_min_size"])
            sim->star_min = dv;
        else if ([key isEqualToString:@"star_max_size"])
            sim->star_max = dv;
        else if ([key isEqualToString:@"background"]) {
            val = [val stringByReplacingOccurrencesOfString:@"\""
                   withString:@""];
            parse_hex([val UTF8String],
                      &sim->bg_r, &sim->bg_g, &sim->bg_b);
        }
        // Zoom
        else if ([key isEqualToString:@"margin"])
            sim->zoom_margin = dv;
        else if ([key isEqualToString:@"damping"])
            sim->damping = dv;
        else if ([key isEqualToString:@"min_scale"])
            sim->min_scale = dv;
        else if ([key isEqualToString:@"max_scale"])
            sim->max_scale = dv;
        // Star fields
        else if (cur_star >= 0) {
            Star *s = &sim->stars[cur_star];
            if ([key isEqualToString:@"mass"]) {
                s->mass = dv;
                s->radius = cbrt(dv);
            } else if ([key isEqualToString:@"position"]) {
                sscanf([val UTF8String], "[%lf, %lf]",
                       &s->x, &s->y);
            } else if ([key isEqualToString:@"velocity"]) {
                sscanf([val UTF8String], "[%lf, %lf]",
                       &s->vx, &s->vy);
            } else if ([key isEqualToString:@"color"]) {
                val = [val stringByReplacingOccurrencesOfString:
                       @"\"" withString:@""];
                parse_hex([val UTF8String],
                          &s->cr, &s->cg, &s->cb);
            }
        }
    }
    // Set tail_len for all stars
    for (int i = 0; i < sim->num_stars; i++)
        sim->stars[i].tail_len = sim->tail_length < MAX_TAIL ?
            sim->tail_length : MAX_TAIL;

    center_frame(sim);
    sim->smooth_scale = 5.0;
    sim->smooth_ox = 0; sim->smooth_oy = 0;
    return sim;
}

@interface ThreeBodySaver : ScreenSaverView {
    Sim *_sim;
}
@end

@implementation ThreeBodySaver

- (instancetype)initWithFrame:(NSRect)frame
                    isPreview:(BOOL)isPreview {
    self = [super initWithFrame:frame isPreview:isPreview];
    if (self) {
        NSBundle *b = [NSBundle bundleForClass:[self class]];
        NSString *cfg = [b pathForResource:@"config"
                                    ofType:@"toml"];
        _sim = load_config(cfg ? cfg : @"");
        [self setAnimationTimeInterval:1.0 / _sim->fps];
    }
    return self;
}

- (void)dealloc {
    if (_sim) free(_sim);
#if !__has_feature(objc_arc)
    [super dealloc];
#endif
}

- (void)animateOneFrame {
    for (int s = 0; s < _sim->steps_per_frame; s++)
        sim_step(_sim);
    [self setNeedsDisplay:YES];
}

- (void)drawRect:(NSRect)rect {
    if (!_sim || _sim->num_stars == 0) return;
    double w = [self bounds].size.width;
    double h = [self bounds].size.height;

    // Background
    [[NSColor colorWithCalibratedRed:_sim->bg_r
        green:_sim->bg_g blue:_sim->bg_b alpha:1] set];
    NSRectFill([self bounds]);

    // Auto-zoom
    double xmin = 1e9, xmax = -1e9;
    double ymin = 1e9, ymax = -1e9;
    for (int i = 0; i < _sim->num_stars; i++) {
        if (_sim->stars[i].x < xmin) xmin = _sim->stars[i].x;
        if (_sim->stars[i].x > xmax) xmax = _sim->stars[i].x;
        if (_sim->stars[i].y < ymin) ymin = _sim->stars[i].y;
        if (_sim->stars[i].y > ymax) ymax = _sim->stars[i].y;
    }
    double cx = (xmax + xmin) / 2.0;
    double cy = (ymax + ymin) / 2.0;
    double span = fmax(fmax(xmax - xmin, ymax - ymin), 10.0);
    double half = span / 2.0 * _sim->zoom_margin;
    double ts = fmin(w, h) / (half * 2.0);
    ts = fmax(_sim->min_scale, fmin(_sim->max_scale, ts));
    double tox = w / 2.0 - cx * ts;
    double toy = h / 2.0 - cy * ts;

    double d = _sim->damping;
    _sim->smooth_scale += (ts - _sim->smooth_scale) * d;
    _sim->smooth_ox += (tox - _sim->smooth_ox) * d;
    _sim->smooth_oy += (toy - _sim->smooth_oy) * d;

    double sc = _sim->smooth_scale;
    double ox = _sim->smooth_ox;
    double oy = _sim->smooth_oy;

    // Draw tails
    for (int i = 0; i < _sim->num_stars; i++) {
        Star *s = &_sim->stars[i];
        if (s->tail_count < 2) continue;
        [[NSColor colorWithCalibratedRed:s->cr
            green:s->cg blue:s->cb alpha:0.6] set];
        NSBezierPath *path = [NSBezierPath bezierPath];
        int idx = s->tail_start;
        double px = s->tail_x[idx] * sc + ox;
        double py = s->tail_y[idx] * sc + oy;
        [path moveToPoint:NSMakePoint(px, py)];
        for (int j = 1; j < s->tail_count; j++) {
            idx = (s->tail_start + j) % s->tail_len;
            px = s->tail_x[idx] * sc + ox;
            py = s->tail_y[idx] * sc + oy;
            [path lineToPoint:NSMakePoint(px, py)];
        }
        [path setLineWidth:1.5];
        [path stroke];
    }

    // Draw stars on top
    for (int i = 0; i < _sim->num_stars; i++) {
        Star *s = &_sim->stars[i];
        double sx = s->x * sc + ox;
        double sy = s->y * sc + oy;
        double sz = s->radius * sc * _sim->star_scale;
        sz = fmax(_sim->star_min, fmin(_sim->star_max, sz));
        [[NSColor colorWithCalibratedRed:s->cr
            green:s->cg blue:s->cb alpha:1] set];
        NSRect r = NSMakeRect(sx - sz, sy - sz,
                              sz * 2, sz * 2);
        [[NSBezierPath bezierPathWithOvalInRect:r] fill];
    }
}

- (BOOL)hasConfigureSheet { return NO; }
- (NSWindow *)configureSheet { return nil; }

@end
