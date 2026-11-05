#!/usr/bin/env python3
"""Check production addon replacement with a vnode_open that leaves old length."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[1]
patches=[root/'patches'/variant/'zzy-native-gpu-addon-mount.patch' for variant in ('xnu','xnu-12377')]
functions=[]
for path in patches:
 added='\n'.join(line[1:] for line in path.read_text().splitlines() if line.startswith('+') and not line.startswith('+++'))
 functions.append('static int\nnative_gpu_addon_write('+added.split('static int\nnative_gpu_addon_write(',1)[1].split('/* Creates the missing parent',1)[0])
assert functions[0]==functions[1]
out=root/'out/check-addon-writer';out.mkdir(parents=True,exist_ok=True)
prefix=r'''
#include <assert.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <fcntl.h>
typedef void *vnode_t;typedef void *vfs_context_t;typedef char *caddr_t;
#define NULLVP NULL
#ifndef FREAD
#define FREAD 1
#define FWRITE 2
#endif
#define UIO_WRITE 1
#define UIO_SYSSPACE 0
#define IO_NOAUTH 0
#define IO_UNIT 0
#define MNT_WAIT 0
struct vnode_attr {uint64_t va_data_size;uint32_t va_mode,active;};
#define VATTR_INIT(p) memset(p,0,sizeof *(p))
#define VATTR_SET(p,member,v) do {(p)->member=(v);(p)->active|=offsetof(struct vnode_attr,member)==0?1:2;} while(0)
static unsigned char file[1024];static size_t file_size;static uint32_t file_mode;
static unsigned writes,closes,attrs,syncs;static int short_write,attr_error,sync_error;
static int vnode_open(const char *p,int flags,int mode,int options,vnode_t *vp,void *ctx) {
 *vp=(void *)1;return 0; /* Deliberately leaves the existing size on O_TRUNC. */
}
static int native_gpu_addon_equal(void *vp,const uint8_t *data,uint64_t n,uint32_t mode,void *ctx) {
 return file_size==n && file_mode==mode && !memcmp(file,data,(size_t)n);
}
static int vnode_close(void *vp,int flags,void *ctx) {closes++;return 0;}
static int vn_rdwr(int op,void *vp,char *data,int n,int offset,int space,int flags,void *cred,int *resid,void *proc) {
 assert(op==UIO_WRITE && offset==0 && n<=(int)sizeof file);writes++;
 int count=n-(short_write?1:0);memcpy(file,data,(size_t)count);if(file_size<(size_t)count)file_size=(size_t)count;
 *resid=n-count;return 0;
}
static int vnode_setattr(void *vp,struct vnode_attr *va,void *ctx) {
 attrs++;if(attr_error)return attr_error;
 if(va->active&1)file_size=(size_t)va->va_data_size;
 if(va->active&2)file_mode=va->va_mode;
 return 0;
}
static int VNOP_FSYNC(void *vp,int wait,void *ctx) {syncs++;return sync_error;}
static void *vfs_context_ucred(void *c) {return c;}
static void *vfs_context_proc(void *c) {return c;}
'''
tests=r'''
int main(void) {
 const uint8_t replacement[]="bplist00-new-cache";const size_t n=sizeof replacement-1;
 memset(file,0x55,sizeof file);file_size=n+55;file_mode=0644;
 assert(!native_gpu_addon_write("cache",replacement,n,0644,NULL));
 assert(file_size==n && !memcmp(file,replacement,n) && writes==1 && attrs==1 && syncs==1 && closes==2);
 assert(native_gpu_addon_write("cache",replacement,n,0644,NULL)==-1 && writes==1);
 file_size=1;assert(!native_gpu_addon_write("cache",replacement,n,0600,NULL) && file_size==n && file_mode==0600);
 assert(!native_gpu_addon_write("cache",replacement,0,0644,NULL) && file_size==0);
 short_write=1;unsigned before=attrs;assert(native_gpu_addon_write("cache",replacement,n,0644,NULL)==EIO && attrs==before);
 short_write=0;attr_error=EACCES;before=syncs;
 assert(native_gpu_addon_write("cache",replacement,n,0644,NULL)==EACCES && syncs==before);
 attr_error=0;sync_error=EIO;file_mode=0600;
 assert(native_gpu_addon_write("cache",replacement,n,0644,NULL)==EIO);
 puts("PASS: stale 55-byte tail removed, exact replacement size/mode, unchanged-file skip, growth, empty file, short write and metadata/sync failures");
}
'''
(out/'test.c').write_text(prefix+functions[0]+tests)
subprocess.run(['clang','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-O1','-g','-fsanitize=address,undefined',str(out/'test.c'),'-o',str(out/'test')],check=True)
r=subprocess.run([out/'test'],capture_output=True,text=True);(out/'output.txt').write_text(r.stdout+r.stderr)
if r.returncode:raise SystemExit(r.stdout+r.stderr)
(out/'report.json').write_text(json.dumps(dict(passed=True,vfs_simulated=True,patches={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in patches},output=r.stdout),indent=2)+'\n')
print(r.stdout,end='')
