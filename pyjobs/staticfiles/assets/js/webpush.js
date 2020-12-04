// Based On https://github.com/chrisdavidmills/push-api-demo/blob/283df97baf49a9e67705ed08354238b83ba7e9d3/main.js

window.addEventListener('load', () => {
  // Do everything if the Browser Supports Service Worker
  if ('serviceWorker' in navigator) {
    const serviceWorker = document.querySelector('meta[name="service-worker-js"]').content;
    navigator.serviceWorker.register(serviceWorker).then((register) => subscribe(register));
  }
});

async function subscribe(register) {
  try {
    const subscription = await register.pushManager.getSubscription();

    if (subscription) return;

    const metaObj = document.querySelector('meta[name="django-webpush-vapid-key"]');
    const applicationServerKey = metaObj.content;
    let options = { userVisibleOnly: true };

    if (applicationServerKey) {
      options.applicationServerKey = urlB64ToUint8Array(applicationServerKey)
    }

    await register.pushManager.subscribe(options);

    console.log('successfully subscription')
  } catch (error) {
    // error
  }
}

function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (var i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}
