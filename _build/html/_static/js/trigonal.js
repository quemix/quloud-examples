
import * as THREE from "./three.module.min.js";
// import { OrbitControls } from "./jsm/control/OrbitControls.js";
import { TrackballControls } from "./jsm/control/TrackballControls.js";

export default function trigonal() {
    const scene = new THREE.Scene();
    // const camera = new THREE.PerspectiveCamera(75, 600/400, 0.1, 1000);
    // const aspect = window.innerWidth / window.innerHeight;
    // const size = 3;
    // const camera = new THREE.OrthographicCamera(
    //     -size * aspect, size * aspect,
    //     size, -size,
    //     0.1, 100,
    // );
    const renderer = new THREE.WebGLRenderer();
    const container = document.getElementById('trigonal');
    container.appendChild(renderer.domElement); // これをやって初めて親要素のサイズが決まる？
    renderer.setSize(container.clientWidth, container.clientHeight);
    const aspect = container.clientWidth / container.clientHeight;
    const size = 3;
    const camera = new THREE.OrthographicCamera(
        -size * aspect, size * aspect,
        size, -size,
        0.1, 100,
    );
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();

    // const geometry = new THREE.BoxGeometry();
    // const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    // const box = new THREE.Mesh(geometry, material);
    // scene.add(box);
    // const geometry = new THREE.BoxGeometry(1, 1, 2);
    // const wireframe = new THREE.WireframeGeometry(geometry);
    // const box = new THREE.LineSegments(wireframe, new THREE.LineBasicMaterial({ color: 0xffffff }));

    // // const geometry = new THREE.BoxGeometry(1, 1, 2);
    // const geometry = new THREE.CylinderGeometry(1, 1, 2, 6);
    // const edges = new THREE.EdgesGeometry(geometry);
    // const positions = edges.attributes.position.array;
    // const numVertices = positions.length / 3;
    // const colors = [];
    // for (let i = 0; i < numVertices; i += 1) {
    //     // デフォルトを白
    //     colors.push(1, 1, 1);
    // }
    // colors[0] = 1; colors[1] = 0; colors[2] = 0; // 頂点1: 赤
    // colors[3] = 1; colors[4] = 0; colors[5] = 0; // 頂点2: 赤
    // edges.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    // const material = new THREE.LineBasicMaterial({ vertexColors: true });
    // const box = new THREE.LineSegments(edges, material);
    // // scene.add(box);
    // const vertices = geometry.attributes.position;
    // const pointMaterial = new THREE.PointsMaterial({
    //     size: 10.0,
    //     color: 0xff0000,
    // });
    // const points = new THREE.Points(geometry, pointMaterial);
    // // scene.add(points);
    const group = new THREE.Group();
    // group.add(box);
    // group.add(points);

    const nx = 1, ny = 1, nz = 1;     // 格子のサイズ
    const dx = 1.0, dy = 1.0, dz = 1.0;  // 格子間隔
    const positions = [];
    const linePositions = [];
    // for (let i = 0; i < nx+1; i++) {
    //     for (let j = 0; j < ny+1; j++) {
    //         for (let k = 0; k < nz+1; k++) {
    //             const x = (i - nx/2) * dx;
    //             const y = (j - ny/2) * dy;
    //             const z = (k - nz/2) * dz;
    //             positions.push(x, y, z);
    //             // x方向に隣接点があれば線を引く
    //             if (i < nx) {
    //                 const x1 = ((i + 1) - nx / 2) * dx;
    //                 linePositions.push(x, y, z, x1, y, z);
    //             }
    //             // y方向に隣接点があれば線を引く
    //             if (j < ny) {
    //                 const y1 = ((j + 1) - ny / 2) * dy;
    //                 linePositions.push(x, y, z, x, y1, z);
    //             }
    //             // z方向に隣接点があれば線を引く
    //             if (k < nz) {
    //                 const z1 = ((k + 1) - nz / 2) * dz;
    //                 linePositions.push(x, y, z, x, y, z1);
    //             }
    //         }
    //     }
    // }

    const a1 = [0.5, 0.86602540378443865, 0.0];
    const a2 = [0.5, -0.86602540378443865, 0.0];
    const a3 = [0.0, 0.0, 1.0]
    for (let i1 = 0; i1 < nx + 1; i1 += 1) {
        for (let j1 = 0; j1 < ny + 1; j1 += 1) {
            for (let k1 = 0; k1 < nz + 1; k1 += 1) {
                const i = i1 - nx / 2;
                const j = j1 - ny / 2;
                const k = k1 - nz / 2;
                const x = a1[0] * i + a2[0] * j + a3[0] * k;
                const y = a1[1] * i + a2[1] * j + a3[1] * k;
                const z = a1[2] * i + a2[2] * j + a3[2] * k;
                positions.push(x, y, z);
                // i方向（a1方向）への線
                if (i < nx - 1) {
                    const x2 = a1[0] * (i + 1) + a2[0] * j + a3[0] * k;
                    const y2 = a1[1] * (i + 1) + a2[1] * j + a3[1] * k;
                    const z2 = a1[2] * (i + 1) + a2[2] * j + a3[2] * k;
                    linePositions.push(x, y, z, x2, y2, z2);
                }
                // j方向（a2方向）への線
                if (j < ny - 1) {
                    const x2 = a1[0] * i + a2[0] * (j + 1) + a3[0] * k;
                    const y2 = a1[1] * i + a2[1] * (j + 1) + a3[1] * k;
                    const z2 = a1[2] * i + a2[2] * (j + 1) + a3[2] * k;
                    linePositions.push(x, y, z, x2, y2, z2);
                }
                // k方向（a3方向）への線
                if (k < nz - 1) {
                    const x2 = a1[0] * i + a2[0] * j + a3[0] * (k + 1);
                    const y2 = a1[1] * i + a2[1] * j + a3[1] * (k + 1);
                    const z2 = a1[2] * i + a2[2] * j + a3[2] * (k + 1);
                    linePositions.push(x, y, z, x2, y2, z2);
                    //  if (i1 === 0 && j1 === 0 && k1 === 0) {
                    //     const origin = new THREE.Vector3(x, y, z);
                    //     const direction = new THREE.Vector3(x2 - x, y2 - y, z2 - z).normalize();
                    //     const length = Math.sqrt((x2 - x) ** 2 + (y2 - y) ** 2 + (z2 - z) ** 2);
                    //     const arrow = new THREE.ArrowHelper(direction, origin, length, 0xff0000, 0.2, 0.1);
                    //     group.add(arrow);
                    // }
                }
            }
        }
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    const material = new THREE.PointsMaterial({
        color: 0x00ffff,
        size: 5.0,
    });
    const points = new THREE.Points(geometry, material);
    group.add(points);

    const lineGeometry = new THREE.BufferGeometry();
    lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0xffffff });
    const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
    group.add(lines);

    // const gridHelper = new THREE.GridHelper(3, 3, 0xffffff);
    // group.add(gridHelper);
    const axesHelper = new THREE.AxesHelper(5);
    group.add(axesHelper);

    camera.position.z = 5;

    scene.add(group);

    // const controls = new OrbitControls(camera, renderer.domElement);
    // controls.enableDamping = true;  // なめらかな操作
    // controls.dampingFactor = 0.05;
    // controls.minPolarAngle = 0;
    // controls.maxPolarAngle = Math.PI * 2;

    const controls = new TrackballControls(camera, renderer.domElement);
    controls.rotateSpeed = 5.0;
    controls.zoomSpeed = 2.2;
    controls.panSpeed = 1.0;
    controls.dynamicDampingFactor = 0.3;

    // const camMarker = new THREE.Mesh(
    //     new THREE.SphereGeometry(0.05, 16, 16),
    //     new THREE.MeshBasicMaterial({ color: 0xff0000 })
    // );
    // scene.add(camMarker);
    // カメラの向きを示す矢印（オプション）
    // const camDir = new THREE.Vector3();
    // const arrow = new THREE.ArrowHelper(camDir, camera.position, 0.3, 0x00ffff);
    // scene.add(arrow);
    // const camHelper = new THREE.CameraHelper(camera);
    // scene.add(camHelper);

    function animate() {
        // console.log(`camera.position: (${camera.position.x.toFixed(2)}, ${camera.position.y.toFixed(2)}, ${camera.position.z.toFixed(2)})`);
        requestAnimationFrame(animate);
        // group.rotation.x += 0.01;
        // group.rotation.y += 0.01;

        // カメラ位置を更新してマーカーを追従
        // camMarker.position.copy(camera.position);
        // カメラの前方方向を取得して矢印更新
        // camera.getWorldDirection(camDir);
        // arrow.setDirection(camDir.clone().normalize());
        // arrow.position.copy(camera.position);

        controls.update();
        renderer.render(scene, camera);
    }

    animate();
}