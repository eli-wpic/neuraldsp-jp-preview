/* Real-time 3D hardware (Three.js), built from the supplied retail photos.
   Each model is a measured config: footprint/height ratios, where the top creases into a slope, which photo
   textures wrap which face, and photo-measured positions of footswitches, knobs and LEDs.
   Nothing unseen is invented — the underside is never shown and there are no exploded views.

   Modes
   - scroll : the stage is pinned while the page scrolls through chapters (homepage Quad Cortex).
   - viewer : a compact stage; view buttons + drag to spin (product pages).
   Vertical page scrolling is never captured; only clearly horizontal drags spin the unit. */
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------------------------------------------------------------- models */
const MODELS = {
  // Quad Cortex: W:D:H(rear) = 1 : 0.655 : 0.166, flat rear 59 %, sloped footswitch deck (front 56 % of rear height)
  qc: {
    W: 3, D: 3 * 0.655, HR: 3 * 0.1656, HF: 3 * 0.1656 * 0.56, VC: 0.59, RAD: 3 * 0.027,
    tex: ['top', 'screen', 'rear'],
    screen: { u0: 0.2334, u1: 0.7666, v0: 0.0942, v1: 0.5495 },
    vents: true,
    switches: [[0.059, 0.695], [0.279, 0.695], [0.5, 0.695], [0.72, 0.695], [0.941, 0.695], [0.059, 0.933], [0.279, 0.933], [0.5, 0.933], [0.72, 0.933], [0.941, 0.933], [0.941, 0.316]],
    knobs: [{ u: 0.104, v: 0.294, r: 0.165, h: 0.13, mark: 0.82 }],
    leds: [[0.059, 0.634, '#f2f2f2'], [0.279, 0.634, '#ff9a1a'], [0.5, 0.634, '#ffc02e'], [0.72, 0.634, '#2f7bff'], [0.059, 0.875, '#ff3b2f'], [0.279, 0.875, '#ffe600'], [0.5, 0.875, '#e24cff'], [0.72, 0.875, '#3dffc0'], [0.941, 0.875, '#6dff4a']],
    views: [
      { pos: [-4.6, 4.3, 6.3], tgt: [0, 0.2, 0], ox: -0.22 },
      { pos: [-0.75, 4.5, 1.95], tgt: [0, 0.45, -0.38], ox: -0.24 },
      { pos: [3.5, 1.05, 3.5], tgt: [0.1, 0.25, 0.5], ox: -0.15 },
      { pos: [3.1, 1.8, -5.2], tgt: [0, 0.22, -0.6], ox: -0.21 },
      { pos: [4.5, 3.9, 6.1], tgt: [0, 0.2, 0], ox: 0.19 },
    ],
  },
  // Quad Cortex mini: flat glass top, W:D:H = 1 : 0.517 : 0.205, four rotary footswitches in the corners
  mini: {
    W: 3, D: 3 * 0.517, HR: 3 * 0.205, HF: 3 * 0.205, VC: 1, RAD: 3 * 0.045,
    tex: ['top', 'rear'], glassTop: true,
    screen: { u0: 0.145, u1: 0.842, v0: 0.118, v1: 0.86 },
    switches: [[0.073, 0.192], [0.914, 0.192], [0.073, 0.804], [0.914, 0.804]],
    knobs: [], leds: [],
    scrollViews: [
      { pos: [-4.4, 4.0, 5.6], tgt: [0, 0.25, 0], ox: -0.22 },
      { pos: [-0.6, 5.4, 2.2], tgt: [0, 0.5, -0.05], ox: -0.24 },
      { pos: [3.4, 2.8, 3.6], tgt: [0.2, 0.35, 0.2], ox: -0.2 },
      { pos: [2.9, 1.8, -5.2], tgt: [0, 0.3, -0.3], ox: -0.22 },
      { pos: [5.1, 3.9, 6.3], tgt: [0, 0.42, 0], ox: 0.2 },
    ],
    views: [
      { pos: [-4.4, 4.0, 5.6], tgt: [0, 0.25, 0], ox: 0 },
      { pos: [0, 6.2, 0.9], tgt: [0, 0.3, 0], ox: 0 },
      { pos: [2.8, 1.6, -4.8], tgt: [0, 0.3, -0.3], ox: 0 },
      { pos: [4.6, 3.6, 5.2], tgt: [0, 0.25, 0], ox: 0 },
    ],
  },
  // Nano Cortex: W:D:H = 1 : 0.687 : 0.312, small front chamfer from 73 % of depth; photos on all four sides
  nano: {
    W: 3, D: 3 * 0.687, HR: 3 * 0.312, HF: 3 * 0.312 * 0.9, VC: 0.73, RAD: 3 * 0.03,
    tex: ['top', 'rear', 'front', 'left', 'right'],
    switches: [[0.091, 0.872], [0.882, 0.872]],
    knobs: [
      { u: 0.118, v: 0.19, r: 0.15, h: 0.3 }, { u: 0.859, v: 0.19, r: 0.15, h: 0.3 },
      { u: 0.223, v: 0.386, r: 0.135, h: 0.28 }, { u: 0.4, v: 0.386, r: 0.135, h: 0.28 }, { u: 0.573, v: 0.392, r: 0.135, h: 0.28 }, { u: 0.755, v: 0.386, r: 0.135, h: 0.28 },
    ],
    buttons: [[0.309, 0.196], [0.486, 0.196], [0.664, 0.196], [0.091, 0.411], [0.882, 0.411]],
    leds: [],
    scrollViews: [
      { pos: [-4.2, 4.4, 5.6], tgt: [0, 0.45, 0], ox: -0.22 },
      { pos: [-0.5, 6.4, 2.4], tgt: [0, 0.8, -0.1], ox: -0.24 },
      { pos: [4.4, 2.0, 4.2], tgt: [0.2, 0.6, 0.4], ox: -0.2 },
      { pos: [3.0, 2.2, -5.8], tgt: [0, 0.5, -0.3], ox: -0.22 },
      { pos: [4.4, 4.2, 5.6], tgt: [0, 0.45, 0], ox: 0.19 },
    ],
    views: [
      { pos: [-4.2, 4.4, 5.6], tgt: [0, 0.45, 0], ox: 0 },
      { pos: [0, 6.6, 1.2], tgt: [0, 0.5, 0], ox: 0 },
      { pos: [2.8, 1.9, -5.0], tgt: [0, 0.4, -0.3], ox: 0 },
      { pos: [5.4, 1.6, 0.6], tgt: [0, 0.4, 0], ox: 0 },
    ],
  },
};

/* ---------------------------------------------------------------- geometry */
function geo(M) {
  const ZB = -M.D / 2, ZF = M.D / 2, ZC = ZB + Math.min(M.VC, 1) * M.D;
  const heightAt = (z) => (M.VC >= 1 || z <= ZC ? M.HR : M.HR + (M.HF - M.HR) * ((z - ZC) / (ZF - ZC)));
  const slope = M.VC >= 1 ? 0 : Math.atan((M.HR - M.HF) / (ZF - ZC));
  const uvToXZ = (u, v) => [(u - 0.5) * M.W, ZB + v * M.D];
  return { ZB, ZF, ZC, heightAt, slope, uvToXZ };
}

function footprint(M, G) {
  const pts = [], seg = 10, R = M.RAD;
  const corner = (cx, cz, a0) => { for (let i = 0; i <= seg; i++) { const a = a0 + (i / seg) * (Math.PI / 2); pts.push([cx + Math.cos(a) * R, cz + Math.sin(a) * R]); } };
  const x0 = -M.W / 2 + R, x1 = M.W / 2 - R, z0 = G.ZB + R, z1 = G.ZF - R;
  corner(x1, z1, 0);
  corner(x0, z1, Math.PI / 2);
  if (M.VC < 1) pts.push([-M.W / 2, G.ZC]);
  corner(x0, z0, Math.PI);
  corner(x1, z0, Math.PI * 1.5);
  if (M.VC < 1) pts.push([M.W / 2, G.ZC]);
  return pts;
}

function wallGeometry(M, G) {
  const pts = footprint(M, G), n = pts.length, pos = [], nor = [], idx = [];
  for (let i = 0; i < n; i++) {
    const [x, z] = pts[i], [xp, zp] = pts[(i - 1 + n) % n], [xn, zn] = pts[(i + 1) % n];
    let nx = zn - zp, nz = -(xn - xp);
    const l = Math.hypot(nx, nz) || 1; nx /= l; nz /= l;
    pos.push(x, 0, z, x, G.heightAt(z), z);
    nor.push(nx, 0, nz, nx, 0, nz);
  }
  for (let i = 0; i < n; i++) { const a = i * 2, b = ((i + 1) % n) * 2; idx.push(a, a + 1, b, b, a + 1, b + 1); }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setIndex(idx);
  return g;
}

function topGeometry(M, G, lift = 0.0015) {
  const xs = [-M.W / 2, M.W / 2];
  const zs = M.VC < 1 ? [G.ZB, G.ZC, G.ZF] : [G.ZB, G.ZF];
  const pos = [], uv = [], idx = [];
  zs.forEach((z) => xs.forEach((x) => { pos.push(x, G.heightAt(z) + lift, z); uv.push((x + M.W / 2) / M.W, 1 - (z - G.ZB) / M.D); }));
  for (let r = 0; r < zs.length - 1; r++) { const a = r * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

function rectOnTop(M, G, r, lift) {
  const x0 = (r.u0 - 0.5) * M.W, x1 = (r.u1 - 0.5) * M.W, z0 = G.ZB + r.v0 * M.D, z1 = G.ZB + r.v1 * M.D;
  const y0 = G.heightAt(z0) + lift, y1 = G.heightAt(z1) + lift;
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute([x0, y0, z0, x1, y0, z0, x0, y1, z1, x1, y1, z1], 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute([r.u0, 1 - r.v0, r.u1, 1 - r.v0, r.u0, 1 - r.v1, r.u1, 1 - r.v1], 2));
  g.setIndex([0, 2, 1, 1, 2, 3]);
  g.computeVertexNormals();
  return g;
}

function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const ventTexture = () => canvasTex(512, 128, (g) => {
  for (let i = 0; i < 30; i++) {
    const x = 8 + i * (496 / 30);
    g.fillStyle = '#050506'; g.beginPath(); g.roundRect(x, 6, 7, 116, 3.5); g.fill();
    g.fillStyle = 'rgba(255,255,255,0.06)'; g.fillRect(x + 7, 8, 1, 112);
  }
});
const glowTexture = () => canvasTex(64, 64, (g) => {
  const r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(0.25, 'rgba(255,255,255,0.45)'); r.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = r; g.fillRect(0, 0, 64, 64);
});
const aoTexture = () => canvasTex(256, 256, (g) => {
  const r = g.createRadialGradient(128, 128, 20, 128, 128, 128);
  r.addColorStop(0, 'rgba(0,0,0,0.85)'); r.addColorStop(0.55, 'rgba(0,0,0,0.45)'); r.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = r; g.fillRect(0, 0, 256, 256);
});

function footswitch(chrome, dark) {
  const g = new THREE.Group();
  const parts = [
    [new THREE.CylinderGeometry(0.074, 0.074, 0.03, 6), chrome, 0.015, Math.PI / 6],
    [new THREE.CylinderGeometry(0.068, 0.07, 0.008, 40), dark, 0.002, 0],
    [new THREE.CylinderGeometry(0.048, 0.05, 0.05, 40), chrome, 0.055, 0],
  ];
  parts.forEach(([geom, mat, y, ry]) => { const m = new THREE.Mesh(geom, mat); m.position.y = y; m.rotation.y = ry; m.castShadow = true; g.add(m); });
  const cap = new THREE.Mesh(new THREE.LatheGeometry([
    new THREE.Vector2(0, 0), new THREE.Vector2(0.054, 0), new THREE.Vector2(0.058, 0.008),
    new THREE.Vector2(0.058, 0.058), new THREE.Vector2(0.052, 0.068), new THREE.Vector2(0, 0.07)], 48), chrome);
  cap.position.y = 0.08; cap.castShadow = true; g.add(cap);
  return g;
}

function knob(k, rubber, mark) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.LatheGeometry([
    new THREE.Vector2(0, 0), new THREE.Vector2(k.r, 0), new THREE.Vector2(k.r, k.h * 0.85),
    new THREE.Vector2(k.r * 0.94, k.h), new THREE.Vector2(0, k.h * 1.01)], 96), rubber);
  body.castShadow = true;
  const line = new THREE.Mesh(new THREE.BoxGeometry(0.008, 0.002, k.r * 0.45), mark);
  line.position.set(0, k.h * 1.012, k.r * 0.5);
  const holder = new THREE.Group(); holder.add(line); holder.rotation.y = Math.PI * (k.mark ?? 0.75);
  g.add(body, holder);
  return g;
}

/* ---------------------------------------------------------------- scene */
export class ND3D {
  constructor(container, modelKey, mode) {
    this.el = container;
    this.M = MODELS[modelKey] || MODELS.qc;
    this.mode = mode;
    this.views = this.M.scrollViews || this.M.views; // same camera moves on the homepage and product pages
    this.canvas = container.querySelector('canvas');
    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, innerWidth < 760 ? 1.6 : 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.scene = new THREE.Scene();
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    this.scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    this.scene.environmentIntensity = 0.45;
    this.camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
    this.progress = 0; this.shown = 0;
    this.spin = 0; this.spinVel = 0; this.dragging = false;
    this.clock = new THREE.Clock();
    this.visible = true;
    this.key = modelKey;
    this.model = null; this.leds = []; this.screenMat = null;
    this.lights();
  }

  /** texture URLs for a model: data-textures (JSON for every model) or data-tex-* (single model) */
  texUrls(key) {
    if (this.el.dataset.textures) return JSON.parse(this.el.dataset.textures)[key] || {};
    const out = {};
    Object.keys(this.el.dataset).filter((k) => k.startsWith('tex')).forEach((k) => { out[k.slice(3).toLowerCase()] = this.el.dataset[k]; });
    return out;
  }

  lights() {
    const key = new THREE.DirectionalLight(0xffffff, 1.7);
    key.position.set(-4, 7, 4.5);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    Object.assign(key.shadow.camera, { left: -3, right: 3, top: 3, bottom: -3, near: 1, far: 20 });
    key.shadow.bias = -0.0004; key.shadow.normalBias = 0.02;
    const rim = new THREE.DirectionalLight(0xa9c8ff, 1.6); rim.position.set(4, 3, -6);
    const warm = new THREE.DirectionalLight(0xffb98a, 0.55); warm.position.set(6, 1.2, 3);
    this.scene.add(key, rim, warm, new THREE.AmbientLight(0xffffff, 0.08));
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.ShadowMaterial({ opacity: 0.5 }));
    ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; this.scene.add(ground);
  }

  async load() {
    await this.setModel(this.key);
    this.resize(); this.bind(); this.loop();
    return this;
  }

  /** build (or swap to) a model in place; rapid switches only keep the latest request */
  async setModel(key) {
    const token = (this._tok = (this._tok || 0) + 1);
    const M = MODELS[key] || MODELS.qc, G = geo(M);
    const urls = this.texUrls(key);
    const group = new THREE.Group();
    const tl = new THREE.TextureLoader();
    const T = {};
    if (this.model) this.el.classList.add('is-swapping');
    await Promise.all(M.tex.map(async (k) => {
      const url = urls[k];
      const t = await tl.loadAsync(url);
      t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = this.renderer.capabilities.getMaxAnisotropy();
      T[k] = t;
    }));

    if (token !== this._tok) return;
    const body = new THREE.MeshPhysicalMaterial({ color: 0x1d1e21, metalness: 0.75, roughness: 0.4, clearcoat: 0.25, clearcoatRoughness: 0.45 });
    const chrome = new THREE.MeshPhysicalMaterial({ color: 0xc9cdd2, metalness: 1, roughness: 0.2 });
    const darkMetal = new THREE.MeshStandardMaterial({ color: 0x18191b, metalness: 0.6, roughness: 0.5 });
    const rubber = new THREE.MeshPhysicalMaterial({ color: 0x141416, metalness: 0.15, roughness: 0.62, sheen: 0.3 });
    const mark = new THREE.MeshBasicMaterial({ color: 0xd8d8d8 });
    const photo = (map, emissive = 0.18, extra = {}) => new THREE.MeshStandardMaterial({ map, alphaTest: 0.5, roughness: 0.6, metalness: 0.2, envMapIntensity: 0.35, emissive: 0xffffff, emissiveMap: map, emissiveIntensity: emissive, ...extra });

    const walls = new THREE.Mesh(wallGeometry(M, G), body); walls.castShadow = true;
    const top = new THREE.Mesh(topGeometry(M, G), photo(T.top, M.glassTop ? 0.3 : 0.22, M.glassTop ? { roughness: 0.15, metalness: 0.1 } : { roughness: 0.72, metalness: 0.1 }));
    top.castShadow = true; top.receiveShadow = true;
    const bottom = new THREE.Mesh(new THREE.PlaneGeometry(M.W - M.RAD, M.D - M.RAD), darkMetal);
    bottom.rotation.x = Math.PI / 2; bottom.position.y = 0.001;
    group.add(walls, top, bottom);

    // display: photographed UI shown unlit (it is a light source)
    let screenMat = null;
    if (M.screen) {
      screenMat = new THREE.MeshBasicMaterial({ map: T.screen || T.top, toneMapped: false, color: new THREE.Color(0.86, 0.86, 0.86) });
      group.add(new THREE.Mesh(rectOnTop(M, G, T.screen ? { u0: M.screen.u0, u1: M.screen.u1, v0: M.screen.v0, v1: M.screen.v1, full: true } : M.screen, 0.004), screenMat));
      if (T.screen) { // dedicated screen texture covers the whole rect
        const g = group.children[group.children.length - 1].geometry;
        g.setAttribute('uv', new THREE.Float32BufferAttribute([0, 1, 1, 1, 0, 0, 1, 0], 2));
      }
    }

    // side photos as decals (alpha keeps the real silhouette, including the front chamfer)
    const face = (map, w, h, pos, ry) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), photo(map, 0.14, { roughness: 0.5, metalness: 0.3 })); m.position.set(...pos); m.rotation.y = ry; group.add(m); };
    if (T.rear) face(T.rear, M.W, M.HR, [0, M.HR / 2, G.ZB - 0.002], Math.PI);
    if (T.front) face(T.front, M.W, M.HF, [0, M.HF / 2, G.ZF + 0.002], 0);
    if (T.left) face(T.left, M.D, M.HR, [-M.W / 2 - 0.002, M.HR / 2, 0], -Math.PI / 2);
    if (T.right) face(T.right, M.D, M.HR, [M.W / 2 + 0.002, M.HR / 2, 0], Math.PI / 2);

    if (M.vents) {
      const ventMat = new THREE.MeshStandardMaterial({ map: ventTexture(), transparent: true, roughness: 0.7, metalness: 0.2, depthWrite: false });
      const vLen = 0.36 * M.D, vH = 0.55 * M.HR, vZ = G.ZB + 0.12 * M.D + vLen / 2;
      [-1, 1].forEach((s) => { const v = new THREE.Mesh(new THREE.PlaneGeometry(vLen, vH), ventMat); v.position.set(s * (M.W / 2 + 0.002), M.HR * 0.46, vZ); v.rotation.y = s * Math.PI / 2; group.add(v); });
    }

    const onTop = (obj, u, v) => {
      const [x, z] = G.uvToXZ(u, v);
      obj.position.set(x, G.heightAt(z), z);
      if (M.VC < 1 && z > G.ZC) obj.rotation.x = G.slope;
      group.add(obj);
    };
    M.switches.forEach(([u, v]) => onTop(footswitch(chrome, darkMetal), u, v));
    M.knobs.forEach((k) => onTop(knob(k, rubber, mark), k.u, k.v));
    (M.buttons || []).forEach(([u, v]) => {
      const b = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.038, 0.03, 32), chrome);
      b.position.y = 0.015; const g = new THREE.Group(); g.add(b); onTop(g, u, v);
    });

    const glow = glowTexture();
    const leds = M.leds.map(([u, v, col], i) => {
      const [x, z] = G.uvToXZ(u, v);
      const y = G.heightAt(z) + 0.006, c = new THREE.Color(col);
      const dot = new THREE.Mesh(new THREE.SphereGeometry(0.016, 16, 12), new THREE.MeshBasicMaterial({ color: c, toneMapped: false }));
      dot.position.set(x, y, z);
      const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, color: c, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.75 }));
      halo.scale.setScalar(0.16); halo.position.set(x, y + 0.01, z);
      group.add(dot, halo);
      return { dot, halo, base: c, i };
    });

    const ao = new THREE.Mesh(new THREE.PlaneGeometry(M.W * 1.35, M.D * 1.55), new THREE.MeshBasicMaterial({ map: aoTexture(), transparent: true, depthWrite: false }));
    ao.rotation.x = -Math.PI / 2; ao.position.y = 0.002; group.add(ao);

    if (token !== this._tok) return;
    if (this.model) {
      this.scene.remove(this.model);
      this.model.traverse((o) => { o.geometry?.dispose(); [].concat(o.material || []).forEach((m) => { m.map?.dispose(); m.dispose(); }); });
    }
    this.model = group; this.scene.add(group);
    Object.assign(this, { M, G, key, views: M.scrollViews || M.views, screenMat, leds, spin: 0, spinVel: 0 });
    requestAnimationFrame(() => this.el.classList.remove('is-swapping'));
  }

  frame(p) {
    const V = this.views, n = V.length - 1;
    const t = reduced ? Math.round(p) : p;
    const i = Math.min(n - 1, Math.floor(t));
    let f = Math.min(1, Math.max(0, t - i)); f = f * f * (3 - 2 * f);
    const a = V[i], b = V[i + 1] || V[i];
    const v3 = (arr) => new THREE.Vector3().fromArray(arr);
    const tgt = v3(a.tgt).lerp(v3(b.tgt), f);
    const sa = new THREE.Spherical().setFromVector3(v3(a.pos).sub(v3(a.tgt)));
    const sb = new THREE.Spherical().setFromVector3(v3(b.pos).sub(v3(b.tgt)));
    let dT = sb.theta - sa.theta; if (dT > Math.PI) dT -= Math.PI * 2; if (dT < -Math.PI) dT += Math.PI * 2;
    const s = new THREE.Spherical(sa.radius + (sb.radius - sa.radius) * f, sa.phi + (sb.phi - sa.phi) * f, sa.theta + dT * f);
    const aspect = this.camera.aspect, portrait = aspect < 1.05;
    if (portrait) s.radius *= Math.max(1.2, 0.9 / aspect);
    else if (this.mode === 'viewer') s.radius *= Math.max(0.92, 1.15 / aspect);
    this.camera.position.setFromSpherical(s).add(tgt);
    this.camera.lookAt(tgt);
    const { w, h } = this.size || { w: 1, h: 1 };
    const ox = portrait || this.mode === 'viewer' ? 0 : (a.ox || 0) + ((b.ox || 0) - (a.ox || 0)) * f;
    const oy = portrait && this.mode === 'scroll' ? 0.2 : 0;
    this.camera.setViewOffset(w, h, ox * w, oy * h, w, h);
  }

  resize() {
    const r = this.el.getBoundingClientRect();
    this.size = { w: r.width, h: r.height };
    this.renderer.setSize(r.width, r.height, false);
    this.camera.aspect = r.width / Math.max(1, r.height);
    this.camera.updateProjectionMatrix();
  }

  bind() {
    new ResizeObserver(() => this.resize()).observe(this.el);
    new IntersectionObserver(([e]) => { this.visible = e.isIntersecting; if (this.visible) this.loop(); }).observe(this.el);
    this.canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); this.el.classList.add('is-fallback'); });
    let sx = 0, sy = 0, lx = 0, lt = 0, mode = null, id = null;
    const el = this.el;
    el.addEventListener('pointerdown', (e) => { if (e.button !== 0 || e.target.closest('a,button')) return; sx = lx = e.clientX; sy = e.clientY; lt = performance.now(); mode = 'pending'; id = e.pointerId; });
    el.addEventListener('pointermove', (e) => {
      if (e.pointerId !== id || !mode) return;
      const dx = e.clientX - sx, dy = e.clientY - sy;
      if (mode === 'pending') {
        if (Math.abs(dx) > 6 && Math.abs(dx) > Math.abs(dy) * 1.2) { mode = 'drag'; this.dragging = true; el.setPointerCapture(id); el.classList.add('is-dragging'); this.onFirstDrag?.(); }
        else if (Math.abs(dy) > 10) { mode = null; return; } else return;
      }
      const now = performance.now(), step = (e.clientX - lx) * 0.008;
      this.spin += step; this.spinVel = (step / Math.max(1, now - lt)) * 16; lx = e.clientX; lt = now;
    });
    const end = (e) => { if (e.pointerId !== id) return; mode = null; id = null; this.dragging = false; el.classList.remove('is-dragging'); };
    el.addEventListener('pointerup', end); el.addEventListener('pointercancel', end);
  }

  setProgress(p) { this.progress = p; }

  loop() {
    if (this._raf) return;
    const tick = () => {
      this._raf = null;
      if (!this.visible) return;
      const dt = Math.min(0.05, this.clock.getDelta()), time = this.clock.elapsedTime;
      this.shown += (this.progress - this.shown) * (reduced ? 1 : Math.min(1, dt * (this.mode === 'viewer' ? 5 : 7)));
      this.frame(this.shown);
      if (!this.dragging) {
        this.spin += this.spinVel; this.spinVel *= reduced ? 0 : 0.92;
        if (Math.abs(this.progress - this.shown) > 0.01 && Math.abs(this.spinVel) < 0.001) this.spin *= 0.9;
      }
      if (this.model) this.model.rotation.y = this.spin;
      const near = (c) => Math.max(0, 1 - Math.abs(this.shown - c) * 1.6);
      if (this.screenMat) this.screenMat.color.setScalar(0.86 + near(1) * 0.14);
      const chase = this.mode === 'scroll' ? near(2) : 0;
      this.leds.forEach((l) => {
        const phase = reduced ? 1 : 0.5 + 0.5 * Math.sin(time * 4 - l.i * 0.7);
        const k = 1 - chase + chase * (0.25 + 0.75 * phase);
        l.halo.material.opacity = 0.25 + 0.6 * k;
        l.dot.material.color.copy(l.base).multiplyScalar(0.55 + 0.6 * k);
      });
      this.renderer.render(this.scene, this.camera);
      this._raf = requestAnimationFrame(tick);
    };
    this._raf = requestAnimationFrame(tick);
  }
}

const webgl = (() => { try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch { return false; } })();

/* ---------------------------------------------------------------- scroll mode (homepage) */
/* The hero can hold several items (3D product stories and campaigns). The dock switches between them:
   the 3D model swaps in place, a photo/video campaign replaces the canvas, and the scroll length follows
   the item (5 chapters for a product story, one screen for a campaign). */
function initScroll(sec) {
  const stage = sec.querySelector('[data-3d-stage]');
  const items = [...sec.querySelectorAll('[data-item]')];
  const docks = [...sec.querySelectorAll('[data-dock-item]')];
  const medias = [...sec.querySelectorAll('[data-media]')];
  let cur = items.find((x) => !x.hidden) || items[0] || sec;
  let chapters = [], pills = [], n = 0, view = null;
  const collect = () => {
    chapters = [...cur.querySelectorAll('[data-chapter]')];
    pills = [...cur.querySelectorAll('[data-goto]')];
    n = Math.max(0, chapters.length - 1);
  };
  // the story finishes at HOLD of the scroll length; the rest keeps the last screen (04, awards) on screen before the page moves on
  const HOLD = 0.8;
  const progress = () => { if (!n) return 0; const r = sec.getBoundingClientRect(); return Math.max(0, Math.min(1, -r.top / Math.max(1, (r.height - innerHeight) * HOLD))) * n; };
  const update = () => {
    const p = progress(); view?.setProgress(p);
    const active = Math.round(p);
    chapters.forEach((c, i) => {
      c.style.opacity = Math.max(0, Math.min(1, 1 - Math.abs(p - i) * 2.4));
      c.style.transform = `translateY(${(i - p) * 36}px)`;
      c.inert = i !== active; c.classList.toggle('is-active', i === active);
    });
    pills.forEach((b, i) => b.setAttribute('aria-current', String(i === active)));
    sec.dataset.chapter = active;
    sec.style.setProperty('--p', n ? p / n : 0);
  };
  const goto = (i, behavior) => { const r = sec.getBoundingClientRect(); scrollTo({ top: scrollY + r.top + (n ? (i / n) * (r.height - innerHeight) * HOLD : 0) + (i ? 2 : 0), behavior }); };
  sec.addEventListener('click', (e) => { const b = e.target.closest('[data-goto]'); if (b) goto(+b.dataset.goto, reduced ? 'auto' : 'smooth'); });

  const showMedia = (id) => {
    medias.forEach((m) => { const on = m.dataset.media === id; m.hidden = !on; m.querySelectorAll('video').forEach((v) => (on ? v.play().catch(() => {}) : v.pause())); });
    stage.classList.toggle('is-media', medias.some((m) => m.dataset.media === id));
  };
  const select = (id, focus) => {
    const next = items.find((x) => x.dataset.item === id);
    if (!next || next === cur) return;
    // back to the top of the hero first so the new item starts at its opening view
    const top = scrollY + sec.getBoundingClientRect().top;
    if (scrollY > top + 2) scrollTo({ top, behavior: 'auto' });
    cur.hidden = true; next.hidden = false; cur = next;
    docks.forEach((d) => d.setAttribute('aria-selected', String(d.dataset.dockItem === id)));
    sec.classList.toggle('is-single', next.dataset.kind === 'campaign');
    showMedia(id);
    const model = next.dataset.model;
    if (model && model !== 'none' && view && view.key !== model) { view.setModel(model).then(update); }
    collect(); update();
    if (focus) next.querySelector('.btn, a, h1')?.focus?.({ preventScroll: true });
  };
  docks.forEach((d, i) => {
    d.addEventListener('click', () => select(d.dataset.dockItem));
    d.addEventListener('keydown', (e) => {
      const k = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      if (!k) return;
      const t = docks[(i + k + docks.length) % docks.length]; t.focus(); select(t.dataset.dockItem);
    });
  });

  // the buy pill appears once the hero's own buy button scrolls away, and then stays for the rest of the page
  const buyToggle = () => document.body.classList.toggle('show-buy', scrollY > innerHeight * 0.45 && cur.dataset.kind !== 'campaign');
  collect(); showMedia(cur.dataset.item);
  addEventListener('scroll', () => { update(); buyToggle(); }, { passive: true }); addEventListener('resize', update); update(); buyToggle();
  const q = new URLSearchParams(location.search);
  if (q.get('hero')) { const d = docks.find((x) => x.querySelector('b')?.textContent.trim() === q.get('hero') || x.dataset.dockItem === q.get('hero')); if (d) select(d.dataset.dockItem); }
  const deep = parseInt(q.get('chapter'), 10);
  if (deep >= 0 && deep <= n) { goto(deep, 'auto'); update(); }
  if (!webgl) { stage.classList.add('is-fallback'); return; }
  new ND3D(stage, stage.dataset.model, 'scroll').load().then((v) => {
    view = v; v.onFirstDrag = () => sec.querySelector('[data-drag-hint]')?.classList.add('is-used');
    const m = cur.dataset.model;
    if (m && m !== 'none' && m !== v.key) v.setModel(m);
    update();
    requestAnimationFrame(() => stage.classList.add('is-ready'));
  }).catch((e) => { console.error(e); stage.classList.add('is-fallback'); });
}

/* ---------------------------------------------------------------- viewer mode (product pages) */
function initViewer(sec) {
  const stage = sec.querySelector('[data-3d-stage]');
  const btns = [...sec.querySelectorAll('[data-view]')];
  const caption = sec.querySelector('[data-view-caption]');
  let view = null, cur = 0;
  const set = (i) => {
    cur = i; view?.setProgress(i); if (view) view.spin *= 0.0;
    btns.forEach((b, k) => b.setAttribute('aria-pressed', String(k === i)));
    if (caption) {
      const t = caption.querySelector('[data-view-title]'), x = caption.querySelector('[data-view-text]');
      if (t || x) { if (t) t.textContent = btns[i]?.dataset.title || ''; if (x) x.textContent = btns[i]?.dataset.caption || ''; }
      else caption.textContent = btns[i]?.dataset.caption || '';
    }
  };
  btns.forEach((b, i) => b.addEventListener('click', () => set(i)));
  if (!webgl) { stage.classList.add('is-fallback'); return; }
  const start = () => new ND3D(stage, stage.dataset.model, 'viewer').load().then((v) => {
    view = v; set(cur);
    v.onFirstDrag = () => sec.querySelector('[data-drag-hint]')?.classList.add('is-used');
    requestAnimationFrame(() => stage.classList.add('is-ready'));
  }).catch((e) => { console.error(e); stage.classList.add('is-fallback'); });
  // load the 3D model only when the viewer approaches the viewport
  const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { io.disconnect(); start(); } }, { rootMargin: '400px 0px' });
  io.observe(sec);
}

document.querySelectorAll('[data-3d="scroll"]').forEach(initScroll);
document.querySelectorAll('[data-3d="viewer"]').forEach(initViewer);
