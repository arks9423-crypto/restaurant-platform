self.addEventListener('push', function(event) {
  const data = event.data ? event.data.json() : {};
  const title = data.title || '✅ طلبك جاهز!';
  const options = {
    body: data.body || 'تفضل استلم طلبك من الكيرب سايد 🚗',
    icon: data.icon || '/static/icon.png',
    badge: '/static/icon.png',
    vibrate: [300, 150, 300, 150, 300],
    dir: 'rtl',
    lang: 'ar',
    data: { url: data.url || '/' },
    requireInteraction: true,
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data.url));
});
