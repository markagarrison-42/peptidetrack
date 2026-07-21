content = open('/home/madfella/peptidetrack/static/app.js').read()

old = """async function enableNotifications() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    flash('notif-flash', 'Push notifications not supported on this device', true);
    return;
  }
  try {
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      flash('notif-flash', 'Permission denied — enable in Settings', true);
      return;
    }
    const reg = await navigator.serviceWorker.ready;
    const keyData = await GET('/api/push/vapid-public-key');
    if (!keyData.key) { flash('notif-flash', 'Server config error', true); return; }
    let sub = await reg.pushManager.getSubscription();
    if (sub) await sub.unsubscribe();
    sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(keyData.key),
    });
    await savePushSubscription(sub);
    flash('notif-flash', '✓ Notifications enabled!');
  } catch (err) {
    flash('notif-flash', err.message, true);
  }
}"""

new = """async function enableNotifications() {
  flash('notif-flash', 'Starting...');
  if (!('serviceWorker' in navigator)) { flash('notif-flash', 'No SW support', true); return; }
  if (!('PushManager' in window)) { flash('notif-flash', 'No PushManager', true); return; }
  try {
    flash('notif-flash', 'Requesting permission...');
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') { flash('notif-flash', 'Permission: ' + permission, true); return; }
    flash('notif-flash', 'Getting SW...');
    const reg = await navigator.serviceWorker.ready;
    flash('notif-flash', 'Getting VAPID key...');
    const keyData = await GET('/api/push/vapid-public-key');
    if (!keyData.key) { flash('notif-flash', 'No VAPID key', true); return; }
    flash('notif-flash', 'Subscribing...');
    let sub = await reg.pushManager.getSubscription();
    if (sub) await sub.unsubscribe();
    sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(keyData.key),
    });
    flash('notif-flash', 'Saving subscription...');
    await savePushSubscription(sub);
    flash('notif-flash', 'Notifications enabled!');
  } catch (err) {
    flash('notif-flash', 'Error: ' + err.message, true);
  }
}"""

if old in content:
    content = content.replace(old, new)
    open('/home/madfella/peptidetrack/static/app.js', 'w').write(content)
    print('done')
else:
    print('NOT FOUND')
    # Find where it is
    idx = content.find('async function enableNotifications()')
    print('Found at:', idx)
    if idx >= 0:
        print(repr(content[idx:idx+100]))
