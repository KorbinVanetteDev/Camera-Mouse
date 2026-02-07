const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const inputCanvas = document.createElement("canvas");
const inputCtx = inputCanvas.getContext("2d");

let width = 1280;
let height = 720;

function setSize(w, h) {
  width = w;
  height = h;
  canvas.width = w;
  canvas.height = h;
  inputCanvas.width = w;
  inputCanvas.height = h;
}

video.addEventListener("loadedmetadata", () => {
  if (video.videoWidth && video.videoHeight) {
    setSize(video.videoWidth, video.videoHeight);
  }
});

// Settings
const defaultCubeSize = 160;
const minCubeSize = 80;
const maxCubeSize = 320;
const defaultSphereRadius = 80;
const minSphereRadius = 40;
const maxSphereRadius = 160;
const defaultTriangleSize = 140;
const minTriangleSize = 60;
const maxTriangleSize = 280;
const scaleSpeed = 0.2;

// Shapes
const cubes = [{ x: 320, y: 240, size: defaultCubeSize, grabbed: false, ox: 0, oy: 0 }];
const spheres = [{ x: 520, y: 240, r: defaultSphereRadius, grabbed: false, ox: 0, oy: 0 }];
const triangles = [{ x: 420, y: 360, size: defaultTriangleSize, grabbed: false, ox: 0, oy: 0 }];

let activeType = null;
let activeIndex = null;
let prevHandDist = null;

// Buttons
const addCubeBtn = { x: 20, y: 20, w: 160, h: 50, pressed: false, label: "Add Cube" };
const addSphereBtn = { x: 200, y: 20, w: 170, h: 50, pressed: false, label: "Add Sphere" };
const addTriangleBtn = { x: 390, y: 20, w: 190, h: 50, pressed: false, label: "Add Triangle" };

function drawButton(btn) {
  ctx.fillStyle = btn.pressed ? "rgb(0,200,0)" : "rgb(0,150,0)";
  ctx.fillRect(btn.x, btn.y, btn.w, btn.h);
  ctx.fillStyle = "white";
  ctx.font = "20px sans-serif";
  ctx.fillText(btn.label, btn.x + 10, btn.y + 32);
}

function isInsideRect(x, y, r) {
  return x >= r.x && x <= r.x + r.w && y >= r.y && y <= r.y + r.h;
}

function distance(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
}

function toPixel(landmark) {
  return { x: landmark.x * width, y: landmark.y * height };
}

function pickLeftRight(hands) {
  let left = hands.find(h => h.label === "Left");
  let right = hands.find(h => h.label === "Right");

  if (!left || !right) {
    const unknown = hands.filter(h => !h.label);
    if (unknown.length >= 2) {
      unknown.sort((a, b) => a.x - b.x);
      left = left || unknown[0];
      right = right || unknown[1];
    }
  }
  return { left, right };
}

function addShapes(left, right) {
  const hands = [left, right].filter(Boolean);

  let addClicked = hands.some(h => h.pinching && isInsideRect(h.x, h.y, addCubeBtn));
  if (addClicked && !addCubeBtn.pressed) {
    cubes.push({ x: width * 0.6, y: height * 0.5, size: defaultCubeSize, grabbed: false, ox: 0, oy: 0 });
  }
  addCubeBtn.pressed = addClicked;

  let addSphereClicked = hands.some(h => h.pinching && isInsideRect(h.x, h.y, addSphereBtn));
  if (addSphereClicked && !addSphereBtn.pressed) {
    spheres.push({ x: width * 0.4, y: height * 0.5, r: defaultSphereRadius, grabbed: false, ox: 0, oy: 0 });
  }
  addSphereBtn.pressed = addSphereClicked;

  let addTriangleClicked = hands.some(h => h.pinching && isInsideRect(h.x, h.y, addTriangleBtn));
  if (addTriangleClicked && !addTriangleBtn.pressed) {
    triangles.push({ x: width * 0.7, y: height * 0.6, size: defaultTriangleSize, grabbed: false, ox: 0, oy: 0 });
  }
  addTriangleBtn.pressed = addTriangleClicked;
}

function grabAndMove(right) {
  if (right && right.pinching) {
    if (activeIndex === null) {
      for (let i = cubes.length - 1; i >= 0; i--) {
        const c = cubes[i];
        const half = c.size / 2;
        if (right.x >= c.x - half && right.x <= c.x + half && right.y >= c.y - half && right.y <= c.y + half) {
          activeType = "cube";
          activeIndex = i;
          c.grabbed = true;
          c.ox = c.x - right.x;
          c.oy = c.y - right.y;
          break;
        }
      }
      if (activeIndex === null) {
        for (let i = spheres.length - 1; i >= 0; i--) {
          const s = spheres[i];
          const dx = right.x - s.x;
          const dy = right.y - s.y;
          if (dx * dx + dy * dy <= s.r * s.r) {
            activeType = "sphere";
            activeIndex = i;
            s.grabbed = true;
            s.ox = s.x - right.x;
            s.oy = s.y - right.y;
            break;
          }
        }
      }
      if (activeIndex === null) {
        for (let i = triangles.length - 1; i >= 0; i--) {
          const t = triangles[i];
          const half = t.size / 2;
          if (right.x >= t.x - half && right.x <= t.x + half && right.y >= t.y - half && right.y <= t.y + half) {
            activeType = "triangle";
            activeIndex = i;
            t.grabbed = true;
            t.ox = t.x - right.x;
            t.oy = t.y - right.y;
            break;
          }
        }
      }
    }

    if (activeIndex !== null) {
      if (activeType === "cube") {
        const c = cubes[activeIndex];
        c.x = right.x + c.ox;
        c.y = right.y + c.oy;
      } else if (activeType === "sphere") {
        const s = spheres[activeIndex];
        s.x = right.x + s.ox;
        s.y = right.y + s.oy;
      } else if (activeType === "triangle") {
        const t = triangles[activeIndex];
        t.x = right.x + t.ox;
        t.y = right.y + t.oy;
      }
    }
  } else {
    if (activeIndex !== null) {
      if (activeType === "cube") cubes[activeIndex].grabbed = false;
      if (activeType === "sphere") spheres[activeIndex].grabbed = false;
      if (activeType === "triangle") triangles[activeIndex].grabbed = false;
    }
    activeType = null;
    activeIndex = null;
  }
}

function scaleShape(left) {
  if (left && left.pinching && activeIndex !== null) {
    if (activeType === "cube") {
      const c = cubes[activeIndex];
      const dist = distance(left, c);
      if (prevHandDist !== null) {
        const delta = dist - prevHandDist;
        c.size = Math.max(minCubeSize, Math.min(maxCubeSize, c.size + delta * scaleSpeed));
      }
      prevHandDist = dist;
    } else if (activeType === "sphere") {
      const s = spheres[activeIndex];
      const dist = distance(left, s);
      if (prevHandDist !== null) {
        const delta = dist - prevHandDist;
        s.r = Math.max(minSphereRadius, Math.min(maxSphereRadius, s.r + delta * scaleSpeed));
      }
      prevHandDist = dist;
    } else if (activeType === "triangle") {
      const t = triangles[activeIndex];
      const dist = distance(left, t);
      if (prevHandDist !== null) {
        const delta = dist - prevHandDist;
        t.size = Math.max(minTriangleSize, Math.min(maxTriangleSize, t.size + delta * scaleSpeed));
      }
      prevHandDist = dist;
    }
  } else {
    prevHandDist = null;
  }
}

function drawShapes() {
  for (const c of cubes) {
    ctx.strokeStyle = c.grabbed ? "yellow" : "blue";
    ctx.lineWidth = 6;
    ctx.strokeRect(c.x - c.size / 2, c.y - c.size / 2, c.size, c.size);
  }
  for (const s of spheres) {
    ctx.strokeStyle = s.grabbed ? "yellow" : "blue";
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.stroke();
  }
  for (const t of triangles) {
    ctx.strokeStyle = t.grabbed ? "yellow" : "blue";
    ctx.lineWidth = 6;
    const half = t.size / 2;
    ctx.beginPath();
    ctx.moveTo(t.x, t.y - half);
    ctx.lineTo(t.x - half, t.y + half);
    ctx.lineTo(t.x + half, t.y + half);
    ctx.closePath();
    ctx.stroke();
  }
}

const hands = new Hands({
  locateFile: file => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
});
hands.setOptions({
  maxNumHands: 2,
  modelComplexity: 1,
  minDetectionConfidence: 0.3,
  minTrackingConfidence: 0.3
});

hands.onResults(results => {
  ctx.clearRect(0, 0, width, height);

  // Draw the flipped image (same as Python's cv2.flip before processing)
  ctx.drawImage(results.image, 0, 0, width, height);

  // Draw landmarks like Python
  if (results.multiHandLandmarks) {
    results.multiHandLandmarks.forEach(landmarks => {
      drawConnectors(ctx, landmarks, HAND_CONNECTIONS, { color: "#000000", lineWidth: 2 });
      drawLandmarks(ctx, landmarks, { color: "#ffffff", lineWidth: 2, radius: 4 });
    });
  }

  const handsData = [];
  if (results.multiHandLandmarks) {
    results.multiHandLandmarks.forEach((landmarks, i) => {
      const thumb = toPixel(landmarks[4]);
      const index = toPixel(landmarks[8]);

      const mid = { x: Math.floor((thumb.x + index.x) / 2), y: Math.floor((thumb.y + index.y) / 2) };
      const pinchDist = Math.hypot(thumb.x - index.x, thumb.y - index.y);
      const pinching = pinchDist <= 80;

      const label = results.multiHandedness?.[i]?.classification?.[0]?.label || null;
      handsData.push({ x: mid.x, y: mid.y, pinching, label });

      ctx.fillStyle = pinching ? "green" : "red";
      ctx.beginPath();
      ctx.arc(mid.x, mid.y, 20, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  const { left, right } = pickLeftRight(handsData);

  addShapes(left, right);
  grabAndMove(right);
  scaleShape(left);

  drawShapes();
  drawButton(addCubeBtn);
  drawButton(addSphereBtn);
  drawButton(addTriangleBtn);
});

const camera = new Camera(video, {
  onFrame: async () => {
    // Flip BEFORE sending to MediaPipe (matches Python)
    inputCtx.save();
    inputCtx.scale(-1, 1);
    inputCtx.translate(-width, 0);
    inputCtx.drawImage(video, 0, 0, width, height);
    inputCtx.restore();
    await hands.send({ image: inputCanvas });
  },
  width: 1280,
  height: 720
});

camera.start();