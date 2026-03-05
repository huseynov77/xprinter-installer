import React, { useState, useEffect, useRef } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet,
  StatusBar, ScrollView, TextInput, Alert, Image, AppState
} from 'react-native';
import * as Location from 'expo-location';
import * as TaskManager from 'expo-task-manager';
import * as Battery from 'expo-battery';
import * as Notifications from 'expo-notifications';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SERVER = 'https://gps-server-production-9cef.up.railway.app';
const TASK = 'clopos-bg';
const VERSION = '1.7.0';

Notifications.setNotificationHandler({
  handleNotification: async () => ({ shouldShowAlert: true, shouldPlaySound: false, shouldSetBadge: false }),
});

// GPS göndər — sadə və sürətli
async function sendGPS(workerId, workerName, lat, lng, speed, battery, address) {
  try {
    await fetch(SERVER + '/api/location', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ workerId, workerName, lat, lng, speed, battery, address, timestamp: Date.now() })
    });
  } catch {}
}

// Ünvan — tamamilə ayrı, GPS-i bloklamır
let _addr = '';
let _addrTime = 0;
function updateAddress(lat, lng) {
  if (Date.now() - _addrTime < 20000) return;
  _addrTime = Date.now();
  fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&accept-language=az`,
    { headers: { 'User-Agent': 'CloposTrack/1.7' } })
    .then(r => r.json())
    .then(d => {
      const a = d.address || {};
      const parts = [];
      const st = a.road || a.pedestrian || a.footway;
      if (st) parts.push(st + (a.house_number ? ' ' + a.house_number : ''));
      if (a.suburb || a.neighbourhood) parts.push(a.suburb || a.neighbourhood);
      if (a.city || a.town || a.village) parts.push(a.city || a.town || a.village);
      _addr = parts.join(', ') || `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    })
    .catch(() => { _addr = `${lat.toFixed(4)}, ${lng.toFixed(4)}`; });
}

// Arxa plan task
TaskManager.defineTask(TASK, async ({ data, error }) => {
  if (error || !data?.locations?.length) return;
  const { latitude: lat, longitude: lng, speed } = data.locations[0].coords;
  const wId = await AsyncStorage.getItem('workerId');
  const wName = await AsyncStorage.getItem('workerName');
  if (!wId) return;
  const bat = Math.round((await Battery.getBatteryLevelAsync()) * 100);
  updateAddress(lat, lng);
  await sendGPS(wId, wName, lat, lng, speed ? Math.round(speed * 3.6) : 0, bat, _addr);
});

const C = { primary: '#0052CC', bg: '#F0F4FF', card: '#FFF', text: '#1A1F36', muted: '#8792A2', border: '#E0E8FF' };

function LoginScreen({ onDone }) {
  const [login, setLogin] = useState('');
  const [pass, setPass] = useState('');
  const [loading, setLoading] = useState(false);

  async function doLogin() {
    if (!login.trim() || !pass.trim()) { Alert.alert('Xəta', 'Login və şifrə lazımdır'); return; }
    setLoading(true);
    try {
      const r = await fetch(SERVER + '/api/auth', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login: login.trim(), password: pass.trim() })
      });
      const res = await r.json();
      if (res.ok) {
        await AsyncStorage.multiSet([['workerName', res.name], ['workerId', res.workerId], ['workerRole', res.role || 'İşçi']]);
        onDone(res.name, res.workerId, res.role || 'İşçi');
      } else {
        Alert.alert('Xəta', res.error || 'Login və ya şifrə yanlışdır');
      }
    } catch { Alert.alert('Xəta', 'Serverə qoşulmaq olmadı'); }
    setLoading(false);
  }

  return (
    <View style={ls.wrap}>
      <StatusBar barStyle="light-content" backgroundColor={C.primary} />
      <View style={ls.top}>
        <Image source={require('./assets/icon.png')} style={ls.logo} />
        <Text style={ls.title}>Clopos Track</Text>
        <Text style={ls.sub}>Login və şifrənizi daxil edin</Text>
      </View>
      <View style={ls.form}>
        <Text style={ls.lbl}>LOGIN</Text>
        <TextInput style={ls.inp} placeholder="istifadeci_adi" placeholderTextColor={C.muted} value={login} onChangeText={setLogin} autoCapitalize="none" />
        <Text style={ls.lbl}>ŞİFRƏ</Text>
        <TextInput style={ls.inp} placeholder="••••••••" placeholderTextColor={C.muted} value={pass} onChangeText={setPass} secureTextEntry />
        <TouchableOpacity style={[ls.btn, loading && { opacity: 0.6 }]} onPress={doLogin} disabled={loading}>
          <Text style={ls.btnT}>{loading ? 'Yoxlanır...' : 'Daxil ol'}</Text>
        </TouchableOpacity>
      </View>
      <Text style={ls.copy}>v{VERSION} © 2026 Huseynov</Text>
    </View>
  );
}

export default function App() {
  const [ready, setReady] = useState(false);
  const [wName, setWName] = useState('');
  const [wId, setWId] = useState('');
  const [wRole, setWRole] = useState('');
  const [tracking, setTracking] = useState(false);
  const [bat, setBat] = useState(0);
  const [lastT, setLastT] = useState('--:--');
  const [addr, setAddr] = useState('Məkan müəyyənləşdirilir...');
  const [coords, setCoords] = useState(null);
  const timer = useRef(null);
  const addrTimer = useRef(null);
  const wIdRef = useRef('');
  const wNameRef = useRef('');

  useEffect(() => {
    init();
    Notifications.requestPermissionsAsync().catch(() => {});
    const sub = AppState.addEventListener('change', state => {
      if (state === 'active' && wIdRef.current) {
        AsyncStorage.getItem('isTracking').then(v => {
          if (v === 'true' && !timer.current) {
            timer.current = setInterval(tick, 3000);
          }
        });
      }
    });
    return () => { sub.remove(); clearInterval(timer.current); clearInterval(addrTimer.current); };
  }, []);

  async function init() {
    const n = await AsyncStorage.getItem('workerName');
    const id = await AsyncStorage.getItem('workerId');
    const r = await AsyncStorage.getItem('workerRole');
    const t = await AsyncStorage.getItem('isTracking');
    if (n && id) {
      setWName(n); setWId(id); setWRole(r || 'İşçi');
      wIdRef.current = id; wNameRef.current = n;
      setReady(true);
      if (t === 'true') setTimeout(() => startTracking(true), 500);
    }
    try { setBat(Math.round((await Battery.getBatteryLevelAsync()) * 100)); } catch {}
  }

  // GPS tick — yalnız GPS, ünvan yox
  async function tick() {
    try {
      const loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      const b = Math.round((await Battery.getBatteryLevelAsync()) * 100);
      const lat = loc.coords.latitude;
      const lng = loc.coords.longitude;
      setCoords({ lat, lng });
      setLastT(new Date().toLocaleTimeString('az'));
      setBat(b);
      if (_addr) setAddr(_addr);
      updateAddress(lat, lng); // bloklamadan arxa planda
      await sendGPS(wIdRef.current, wNameRef.current, lat, lng,
        loc.coords.speed ? Math.round(loc.coords.speed * 3.6) : 0, b, _addr);
    } catch {}
  }

  async function startTracking(resume = false) {
    if (!resume) {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') { Alert.alert('GPS icazəsi lazımdır'); return; }
    }
    setTracking(true);
    await AsyncStorage.setItem('isTracking', 'true');
    tick();
    clearInterval(timer.current);
    timer.current = setInterval(tick, 3000);

    // Arxa plan
    Location.requestBackgroundPermissionsAsync().then(async ({ status }) => {
      if (status !== 'granted') return;
      try {
        const has = await TaskManager.isTaskRegisteredAsync(TASK);
        if (has) await Location.stopLocationUpdatesAsync(TASK);
        await Location.startLocationUpdatesAsync(TASK, {
          accuracy: Location.Accuracy.Balanced,
          timeInterval: 3000,
          distanceInterval: 0,
          foregroundService: {
            notificationTitle: '📍 Clopos Track — AKTİV',
            notificationBody: 'İzləmə davam edir. Dayandırmaq üçün tətbiqi açın.',
            notificationColor: '#0052CC',
            killServiceOnDestroy: false,
          },
          pausesUpdatesAutomatically: false,
        });
      } catch {}
    }).catch(() => {});
  }

  async function stopTracking() {
    clearInterval(timer.current); timer.current = null;
    setTracking(false);
    await AsyncStorage.setItem('isTracking', 'false');
    try {
      const has = await TaskManager.isTaskRegisteredAsync(TASK);
      if (has) await Location.stopLocationUpdatesAsync(TASK);
    } catch {}
    try {
      await fetch(SERVER + '/api/status', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workerId: wIdRef.current, online: false })
      });
    } catch {}
    Notifications.scheduleNotificationAsync({
      content: { title: '⚠️ Clopos Track', body: `${wNameRef.current} — izləmə dayandırıldı!` },
      trigger: null
    }).catch(() => {});
  }

  async function logout() {
    await stopTracking();
    await AsyncStorage.clear();
    setReady(false); setWName(''); setWId(''); setWRole('');
  }

  if (!ready) return <LoginScreen onDone={(n, id, r) => {
    setWName(n); setWId(id); setWRole(r);
    wIdRef.current = id; wNameRef.current = n; setReady(true);
  }} />;

  const ini = wName.split(' ').map(x => x[0]).join('').slice(0, 2);
  const bc = bat > 50 ? '#00875A' : bat > 20 ? '#FF8B00' : '#FF4444';

  return (
    <View style={s.wrap}>
      <StatusBar barStyle="light-content" backgroundColor={C.primary} />
      <View style={s.header}>
        <View style={s.logoRow}>
          <Image source={require('./assets/icon.png')} style={s.logoImg} />
          <View>
            <Text style={s.logoTxt}>Clopos Track</Text>
            <Text style={s.logoSub}>İşçi İzləmə Sistemi</Text>
          </View>
        </View>
        <View style={[s.badge, tracking ? s.badgeOn : s.badgeOff]}>
          <View style={[s.dot, { backgroundColor: tracking ? '#00E676' : '#aaa' }]} />
          <Text style={[s.badgeTxt, { color: tracking ? '#00E676' : '#aaa' }]}>{tracking ? 'AKTİV' : 'DEAKTİV'}</Text>
        </View>
      </View>

      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={s.card}>
          <View style={s.avWrap}>
            <View style={s.av}><Text style={s.avT}>{ini}</Text></View>
            <View style={[s.onDot, { backgroundColor: tracking ? '#00E676' : '#ccc' }]} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={s.wName}>{wName}</Text>
            <Text style={s.wRole}>{wRole}</Text>
          </View>
        </View>

        <View style={s.stats}>
          <View style={s.stat}>
            <Text style={s.sIcon}>🔋</Text>
            <Text style={[s.sVal, { color: bc }]}>{bat}%</Text>
            <Text style={s.sLbl}>Batareya</Text>
          </View>
          <View style={[s.stat, s.statMain]}>
            <Text style={s.sIcon}>📡</Text>
            <Text style={[s.sVal, { color: tracking ? '#00E676' : '#ff4444' }]}>{tracking ? 'CANLI' : 'OFF'}</Text>
            <Text style={[s.sLbl, { color: 'rgba(255,255,255,0.7)' }]}>Status</Text>
          </View>
          <View style={s.stat}>
            <Text style={s.sIcon}>🕐</Text>
            <Text style={s.sVal}>{lastT}</Text>
            <Text style={s.sLbl}>Son göndərmə</Text>
          </View>
        </View>

        <View style={s.locCard}>
          <Text style={s.locTitle}>📍 Hal-hazırda olduğunuz ünvan</Text>
          <Text style={s.locAddr}>{addr}</Text>
          {coords && <Text style={s.locCoord}>{coords.lat.toFixed(5)}, {coords.lng.toFixed(5)}</Text>}
        </View>

        <TouchableOpacity style={[s.btn, tracking ? s.stopBtn : s.startBtn]}
          onPress={tracking ? stopTracking : () => startTracking(false)} activeOpacity={0.85}>
          <Text style={s.btnTxt}>{tracking ? 'İzləməni Dayandır' : 'İzləməni Başlat'}</Text>
        </TouchableOpacity>

        <Text style={s.note}>Hər 3 saniyədən bir məkan göndərilir · Arxa planda işləyir</Text>
        <TouchableOpacity style={s.logout} onPress={logout}>
          <Text style={s.logoutT}>Çıxış et</Text>
        </TouchableOpacity>
        <Text style={s.copy}>v{VERSION} © 2026 Huseynov. Müəllif hüququ qorunur.</Text>
      </ScrollView>
    </View>
  );
}

const s = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: C.bg },
  header: { backgroundColor: C.primary, paddingTop: 48, paddingBottom: 20, paddingHorizontal: 20, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  logoRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  logoImg: { width: 36, height: 36, borderRadius: 10 },
  logoTxt: { fontSize: 18, fontWeight: '800', color: '#fff' },
  logoSub: { fontSize: 11, color: 'rgba(255,255,255,0.7)', marginTop: 1 },
  badge: { flexDirection: 'row', alignItems: 'center', gap: 5, paddingHorizontal: 10, paddingVertical: 5, borderRadius: 20, borderWidth: 1 },
  badgeOn: { backgroundColor: 'rgba(0,230,118,0.1)', borderColor: 'rgba(0,230,118,0.3)' },
  badgeOff: { backgroundColor: 'rgba(255,255,255,0.1)', borderColor: 'rgba(255,255,255,0.2)' },
  dot: { width: 6, height: 6, borderRadius: 3 },
  badgeTxt: { fontSize: 11, fontWeight: '700' },
  card: { margin: 16, backgroundColor: C.card, borderRadius: 16, padding: 16, flexDirection: 'row', alignItems: 'center', gap: 14, elevation: 3 },
  avWrap: { position: 'relative' },
  av: { width: 52, height: 52, borderRadius: 14, backgroundColor: C.primary, alignItems: 'center', justifyContent: 'center' },
  avT: { fontSize: 18, fontWeight: '800', color: '#fff' },
  onDot: { position: 'absolute', bottom: -1, right: -1, width: 14, height: 14, borderRadius: 7, borderWidth: 2, borderColor: C.card },
  wName: { fontSize: 16, fontWeight: '700', color: C.text },
  wRole: { fontSize: 12, color: C.muted, marginTop: 3 },
  stats: { flexDirection: 'row', marginHorizontal: 16, gap: 10, marginBottom: 12 },
  stat: { flex: 1, backgroundColor: C.card, borderRadius: 14, padding: 14, alignItems: 'center', elevation: 2 },
  statMain: { backgroundColor: C.primary },
  sIcon: { fontSize: 18, marginBottom: 4 },
  sVal: { fontSize: 16, fontWeight: '800', color: C.text },
  sLbl: { fontSize: 10, color: C.muted, marginTop: 2, textTransform: 'uppercase' },
  locCard: { marginHorizontal: 16, backgroundColor: C.card, borderRadius: 16, padding: 16, marginBottom: 20, elevation: 2 },
  locTitle: { fontSize: 13, fontWeight: '700', color: C.text, marginBottom: 8 },
  locAddr: { fontSize: 14, fontWeight: '600', color: C.text, lineHeight: 22 },
  locCoord: { fontSize: 10, color: C.muted, fontFamily: 'monospace', marginTop: 4 },
  btn: { marginHorizontal: 16, paddingVertical: 18, borderRadius: 16, alignItems: 'center', elevation: 4 },
  startBtn: { backgroundColor: C.primary },
  stopBtn: { backgroundColor: '#FF4444' },
  btnTxt: { fontSize: 16, fontWeight: '800', color: '#fff' },
  note: { textAlign: 'center', color: C.muted, fontSize: 11, marginTop: 14, marginBottom: 6 },
  logout: { alignItems: 'center', padding: 16 },
  logoutT: { color: C.muted, fontSize: 13, textDecorationLine: 'underline' },
  copy: { textAlign: 'center', color: C.muted, fontSize: 10, marginBottom: 32 },
});

const ls = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: C.primary },
  top: { alignItems: 'center', paddingTop: 60, paddingBottom: 40, paddingHorizontal: 32 },
  logo: { width: 100, height: 100, borderRadius: 24, marginBottom: 20 },
  title: { fontSize: 28, fontWeight: '900', color: '#fff', marginBottom: 8 },
  sub: { fontSize: 13, color: 'rgba(255,255,255,0.7)', textAlign: 'center' },
  form: { flex: 1, backgroundColor: C.bg, borderTopLeftRadius: 28, borderTopRightRadius: 28, padding: 28 },
  lbl: { fontSize: 11, color: C.muted, fontWeight: '700', letterSpacing: 1, marginBottom: 6, textTransform: 'uppercase' },
  inp: { backgroundColor: C.card, borderWidth: 1.5, borderColor: C.border, borderRadius: 12, padding: 14, fontSize: 15, color: C.text, marginBottom: 16 },
  btn: { backgroundColor: C.primary, paddingVertical: 16, borderRadius: 14, alignItems: 'center', marginTop: 8 },
  btnT: { fontSize: 16, fontWeight: '800', color: '#fff' },
  copy: { textAlign: 'center', color: 'rgba(255,255,255,0.4)', fontSize: 10, paddingBottom: 24, paddingTop: 16 },
});
