content = open('/home/madfella/peptidetrack/static/app.js').read()

old = """    flash('notif-flash', 'Getting SW...');
    const reg = await navigator.serviceWorker.ready;
    flash('notif-flash', 'Getting VAPID key...');"""

new = """    flash('notif-flash', 'Getting SW...');
    let reg = null;
    try {
      const swRegs = await navigator.serviceWorker.getRegistrations();
      if (swRegs.length > 0) {
        reg = swRegs[0];
      } else {
        reg = await navigator.serviceWorker.register('/static/sw.js');
        await new Promise(function(resolve) { setTimeout(resolve, 1000); });
      }
    } catch(swErr) {
      flash('notif-flash', 'SW error: ' + swErr.message, true);
      return;
    }
    if (!reg) { flash('notif-flash', 'No SW registration', true); return; }
    flash('notif-flash', 'Getting VAPID key...');"""

if old in content:
    content = content.replace(old, new)
    open('/home/madfella/peptidetrack/static/app.js', 'w').write(content)
    print('done')
else:
    print('NOT FOUND')
    idx = content.find('Getting SW')
    print('Found at:', idx)
    print(repr(content[idx:idx+200]))
