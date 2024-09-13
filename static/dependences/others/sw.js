self.addEventListener('install', event => {
  console.log("installing…");
});

self.addEventListener('activate', event => {
  console.log("activated.");
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  self.update()

  // serve the horse SVG from the cache if the request is
  // same-origin
  if (url.origin == location.origin) {
    if(url in caches){
      event.respondWith(caches.match(url));
    }else{
      caches.open('hswm-sw1').then(cache => {
        cache.add(url)
      })
    }
  }
});