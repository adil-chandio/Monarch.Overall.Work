/* Minimal libXfixes stand-in: Blender references the cursor API at link time. */
#include <stddef.h>
typedef struct _XDisplay Display;
int  XFixesQueryExtension(Display *d, int *e, int *b) { (void)d; if (e) *e = 0; if (b) *b = 0; return 0; }
int  XFixesQueryVersion(Display *d, int *maj, int *min) { (void)d; if (maj) *maj = 0; if (min) *min = 0; return 0; }
void XFixesShowCursor(Display *d, unsigned long c) { (void)d; (void)c; }
void XFixesHideCursor(Display *d, unsigned long c) { (void)d; (void)c; }
unsigned long XFixesCreateRegion(Display *d, void *rects, int n) { (void)d; (void)rects; (void)n; return 0; }
void XFixesDestroyRegion(Display *d, unsigned long r) { (void)d; (void)r; }
void XFixesSetCursorName(Display *d, unsigned long c, const char *n) { (void)d; (void)c; (void)n; }
