/* Minimal libXrender stand-in for headless Blender.
 *
 * Blender 4.2's bundled lib links the Xrender client library for the windowed
 * build. Offline rendering never composites through X, so these stubs are never
 * called on the render path; they exist so the dynamic loader can resolve them.
 *
 * Every function returns 0/NULL and sets no state. This is NOT an X11
 * implementation: do not use it for anything that opens a display.
 */
#include <stddef.h>

typedef struct _XDisplay Display;
typedef unsigned long XID;

typedef struct {
    short red, red_mask;
    short green, green_mask;
    short blue, blue_mask;
    short alpha, alpha_mask;
} XRenderPictFormat;

int XRenderQueryExtension(Display *dpy, int *event_base, int *error_base) {
    if (event_base) *event_base = 0;
    if (error_base) *error_base = 0;
    return 0;                      /* "not supported" — a clean refusal */
}

int XRenderQueryVersion(Display *dpy, int *major, int *minor) {
    if (major) *major = 0;
    if (minor) *minor = 0;
    return 0;
}

XRenderPictFormat *XRenderFindVisualFormat(Display *dpy, void *visual) {
    (void)dpy; (void)visual;
    return NULL;
}

XRenderPictFormat *XRenderFindStandardFormat(Display *dpy, int fmt) {
    (void)dpy; (void)fmt;
    return NULL;
}

int XRenderSetPictureTransform(Display *dpy, XID picture, void *transform) {
    (void)dpy; (void)picture; (void)transform;
    return 0;
}
