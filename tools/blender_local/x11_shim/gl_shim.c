/* Minimal libGL/libEGL stand-ins for headless rendering.
 *
 * Blender's bundled modules (libusd_ms, the GPU backend) reference the GL client
 * library at link time. Offline Cycles/EEVEE rendering in a container never owns a
 * GL context, so these stubs satisfy the loader and return "nothing available".
 * They are deliberately NOT an OpenGL implementation.
 */
#include <stddef.h>

typedef struct _XDisplay Display;
typedef unsigned long GLXDrawable;
typedef void *GLXContext;
typedef void *GLXFBConfig;

void *glXGetProcAddress(const unsigned char *n) { (void)n; return NULL; }
void *glXGetProcAddressARB(const unsigned char *n) { (void)n; return NULL; }
int   glXQueryExtension(Display *d, int *e, int *v) { (void)d; if (e) *e = 0; if (v) *v = 0; return 0; }
int   glXQueryVersion(Display *d, int *maj, int *min) { (void)d; if (maj) *maj = 0; if (min) *min = 0; return 0; }
void *glXChooseVisual(Display *d, int s, int *a) { (void)d; (void)s; (void)a; return NULL; }
GLXContext glXCreateNewContext(Display *d, GLXFBConfig c, int t, GLXContext sh, int dir) {
    (void)d; (void)c; (void)t; (void)sh; (void)dir; return NULL;
}
GLXContext glXCreateContext(Display *d, void *vi, GLXContext sh, int dir) {
    (void)d; (void)vi; (void)sh; (void)dir; return NULL;
}
int   glXMakeCurrent(Display *d, GLXDrawable w, GLXContext c) { (void)d; (void)w; (void)c; return 0; }
int   glXMakeContextCurrent(Display *d, GLXDrawable dr, GLXDrawable re, GLXContext c) {
    (void)d; (void)dr; (void)re; (void)c; return 0;
}
void  glXDestroyContext(Display *d, GLXContext c) { (void)d; (void)c; }
GLXDrawable glXGetCurrentDrawable(void) { return 0; }
GLXContext  glXGetCurrentContext(void) { return NULL; }
Display    *glXGetCurrentDisplay(void) { return NULL; }
void  glXSwapBuffers(Display *d, GLXDrawable w) { (void)d; (void)w; }
int   glXSwapIntervalEXT(Display *d, GLXDrawable w, int i) { (void)d; (void)w; (void)i; return 0; }
void  glXWaitX(void) {}
void  glXWaitGL(void) {}
void *glXGetSelectedEvent(Display *d, GLXDrawable w, unsigned long *m) { (void)d; (void)w; (void)m; return NULL; }

void *glXGetVisualFromFBConfig(Display *d, GLXFBConfig c) { (void)d; (void)c; return NULL; }
GLXFBConfig *glXChooseFBConfig(Display *d, int s, const int *a, int *n) {
    (void)d; (void)s; (void)a; if (n) *n = 0; return NULL;
}
GLXFBConfig *glXGetFBConfigs(Display *d, int s, int *n) { (void)d; (void)s; if (n) *n = 0; return NULL; }
int glXGetFBConfigAttrib(Display *d, GLXFBConfig c, int a, int *v) { (void)d; (void)c; (void)a; if (v) *v = 0; return 0; }
void *glXCreatePbuffer(Display *d, GLXFBConfig c, const int *a) { (void)d; (void)c; (void)a; return NULL; }
void *glXCreateWindow(Display *d, GLXFBConfig c, unsigned long w, const int *a) {
    (void)d; (void)c; (void)w; (void)a; return NULL;
}
void glXDestroyPbuffer(Display *d, void *p) { (void)d; (void)p; }
void glXDestroyWindow(Display *d, void *w) { (void)d; (void)w; }
void glXQueryDrawable(Display *d, GLXDrawable w, int a, unsigned int *v) { (void)d; (void)w; (void)a; if (v) *v = 0; }
int  glXBindTexImageEXT(Display *d, GLXDrawable w, int buf, const int *a) { (void)d; (void)w; (void)buf; (void)a; return 0; }
void glXReleaseTexImageEXT(Display *d, GLXDrawable w, int buf) { (void)d; (void)w; (void)buf; }

/* Core GL 1.x entry points referenced by Blender's bundled USD/GPU modules.
   All are no-ops: nothing on the headless render path queries a live GL context. */
void glFinish(void) {}
void glFlush(void) {}
void glGetIntegerv(unsigned int p, int *v) { (void)p; if (v) *v = 0; }
void glGetFloatv(unsigned int p, float *v) { (void)p; if (v) *v = 0.0f; }
void glGetString(unsigned int n) { (void)n; }
void glGetError(void) { }
void glPixelStorei(unsigned int p, int v) { (void)p; (void)v; }
void glReadPixels(int x, int y, int w, int h, unsigned int f, unsigned int t, void *d) {
    (void)x; (void)y; (void)w; (void)h; (void)f; (void)t; (void)d;
}
void glViewport(int x, int y, int w, int h) { (void)x; (void)y; (void)w; (void)h; }
void glEnable(unsigned int c) { (void)c; }
void glDisable(unsigned int c) { (void)c; }
void glClear(unsigned int m) { (void)m; }
void glClearColor(float r, float g, float b, float a) { (void)r; (void)g; (void)b; (void)a; }
int glXQueryContext(Display *d, GLXContext c, int a, int *v) { (void)d; (void)c; (void)a; if (v) *v = 0; return 0; }
int glXIsDirect(Display *d, GLXContext c) { (void)d; (void)c; return 1; }
void *glXAllocateMemoryNV(long s, float a, float b, float c) { (void)s; (void)a; (void)b; (void)c; return NULL; }
void glXFreeMemoryNV(void *p) { (void)p; }
