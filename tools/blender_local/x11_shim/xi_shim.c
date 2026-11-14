/* Minimal libXi stand-in for headless Blender (XInput2 symbols at link time). */
#include <stddef.h>
typedef struct _XDisplay Display;
int  XQueryExtension(Display *d, const char *n, int *op, int *ev, int *er) {
    (void)d; (void)n; if (op) *op = 0; if (ev) *ev = 0; if (er) *er = 0; return 0;
}
int  XIQueryVersion(Display *d, int *maj, int *min) { (void)d; if (maj) *maj = 0; if (min) *min = 0; return 0; }
void XCloseDevice(Display *d, void *dev) { (void)d; (void)dev; }
void *XIQueryDevice(Display *d, int id, int *n) { (void)d; (void)id; if (n) *n = 0; return NULL; }
void XIFreeDeviceInfo(void *info) { (void)info; }
void XSelectInput(Display *d, unsigned long w, long m) { (void)d; (void)w; (void)m; }
