=======================================
BaTiO₃格子定数の計算例
=======================================

.. raw:: html

   <style>
   .table-scroll {
       width: 100%;
       overflow-x: auto;
       margin: 1.0em 0 1.2em 0;
       padding-bottom: 0.15em;
   }
   .slide-style-table,
   .color-guide-horizontal {
       width: 100%;
       border-collapse: collapse;
       table-layout: fixed;
   }
   .slide-style-table {
       font-size: 0.92em;
       line-height: 1.35;
       border: 1px solid #d0d7de;
       border-radius: 10px;
       box-shadow: 0 1px 2px rgba(27, 31, 36, 0.04);
       background: #ffffff;
   }
   .table-lattice {
       min-width: 1380px;
   }
   .table-error {
       min-width: 1320px;
   }
   .slide-style-table caption {
       caption-side: top;
       text-align: left !important;
       font-weight: 700;
       margin: 0 0 0.35em 0;
       padding: 0.1em 0.05em 0.35em 0.05em;
       color: #24292f;
       background: transparent;
       border: 0;
       border-radius: 0;
       letter-spacing: 0.01em;
   }
   .slide-style-table th {
       background: #f6f8fa;
       color: #24292f;
       font-weight: 700;
       text-align: center !important;
       vertical-align: middle !important;
       border: 1px solid #c9d1d9;
       padding: 0.72em 0.42em;
       overflow-wrap: normal;
       word-break: keep-all;
   }
   .slide-style-table .group-header {
       background: #eef0f3;
       color: #24292f;
       font-weight: 700;
   }
   .slide-style-table td {
       text-align: center !important;
       vertical-align: middle !important;
       border: 1px solid #d8dee4;
       padding: 0.58em 0.35em;
       overflow-wrap: normal;
       word-break: keep-all;
       background-clip: padding-box;
   }
   .slide-style-table .phase-cell,
   .slide-style-table .method-cell,
   .slide-style-table .parameter-cell {
       background-color: #ffffff;
       color: #24292f;
       font-weight: 650;
   }
   .slide-style-table .value-cell {
       background-color: #ffffff;
   }
   .slide-style-table tbody tr:hover td:not(.err-green):not(.err-yellow):not(.err-orange):not(.err-red):not(.error-multi) {
       background-color: #f6f8fa;
   }
   .err-green {
       background-color: #d9ead3;
   }
   .err-yellow {
       background-color: #fff2cc;
   }
   .err-orange {
       background-color: #fce5cd;
   }
   .err-red {
       background-color: #f4cccc;
   }
   .error-multi {
       background-color: transparent !important;
       padding: 0 !important;
       vertical-align: stretch !important;
   }
   .error-multi .err-subrow {
       display: flex;
       align-items: center;
       justify-content: center;
       width: 100%;
       min-height: 2.15em;
       margin: 0;
       padding: 0.28em 0.20em;
       box-sizing: border-box;
       border-radius: 0;
   }
   .error-multi .err-subrow + .err-subrow {
       border-top: 1px solid #d6dde6;
   }
   .ref-cell {
       line-height: 1.45;
       padding: 0 !important;
   }
   .ref-cell .ref-subrow {
       display: flex;
       align-items: center;
       justify-content: center;
       width: 100%;
       min-height: 2.15em;
       margin: 0;
       padding: 0.28em 0.20em;
       box-sizing: border-box;
   }
   .ref-cell .ref-subrow + .ref-subrow {
       border-top: 1px solid #d6dde6;
   }
   .color-guide-title {
       margin-top: 0.8em;
       margin-bottom: 0.35em;
       font-weight: 700;
   }
   .color-guide-horizontal {
       margin: 0.4em 0 1.2em 0;
   }
   .color-guide-horizontal th,
   .color-guide-horizontal td {
       text-align: center !important;
       vertical-align: middle !important;
       border: 1px solid #d9dee5;
       padding: 0.55em 0.75em;
       font-weight: 600;
   }
   </style>

本節では、BaTiO₃の各強誘電相における格子定数について、可変セル最適化により得られた計算値を実験値と比較する。
実験値は各相が安定に存在する温度領域における代表値であり、一方で計算値は0 Kにおける最適化構造に対応する。
したがって、両者の比較は定量的な一致のみを評価するものではなく、熱膨張や相安定性の温度依存性を考慮した定性的な比較として扱う必要がある。

格子最適化に用いた入力ファイル例
--------------------------------

ここでは、各相の結晶対称性を保ったまま格子定数を調整するための代表的な入力例を示す。Quloud Jobで利用する場合は、下のブロックを展開してコピーし、対応する入力ファイルを置き換える。OpenMXでは ``openmx.in``、QEでは ``QuloudJob.scf.in``、ASEでは ``ase.in``、LAMMPSでは ``in.QuloudJob`` を使用する。

格子のみを比較したい場合は、内部座標を固定し、相ごとに許される格子自由度だけを動かす必要がある。例えば、立方晶では :math:`a=b=c` を保つ必要があり、正方晶では :math:`a=b` を保ったまま :math:`c` を独立に変化させる。斜方晶では直交角を保って :math:`a`、:math:`b`、:math:`c` を独立に変化させ、菱面体晶では :math:`a=b=c` と菱面体晶の角度関係を保つ。

そのため、OpenMXでは相に応じて ``OptC3``、``OptC4``、``OptC2`` を使い分けた。これは、最適化の途中で立方晶、正方晶、斜方晶、菱面体晶の特徴が混ざったり、別の相へ崩れたりすることを避けるためである。QEでは同じ考え方を ``vc-relax`` と ``cell_dofree = 'ibrav'`` により実装した。MLIPのASE/LAMMPS入力は、同じ構造ファイルに対してセルを含む緩和を行うための例として示した。

各ブロックは折りたたみ形式で表示される。相名または手法名をクリックすると入力内容が縦方向に展開され、右上のコピーアイコンから全文を取得できる。

入力ファイルの対応
~~~~~~~~~~~~~~~~~~

.. list-table:: 相ごとのセル拘束
   :header-rows: 1
   :widths: 18 18 22 42

   * - 相
     - OpenMX
     - QE
     - 保持する格子の特徴
   * - 立方晶
     - ``OptC3``
     - ``ibrav=1``
     - :math:`a=b=c`、角度90°
   * - 正方晶
     - ``OptC4``
     - ``ibrav=6``
     - :math:`a=b`、:math:`c` は独立
   * - 斜方晶
     - ``OptC2``
     - ``ibrav=8``
     - 角度90°、:math:`a,b,c` は独立
   * - 菱面体晶
     - ``OptC3``
     - ``ibrav=5``
     - :math:`a=b=c` と菱面体晶角

.. raw:: html

   <style>
   .input-toggle {
       border: 1px solid #d0d7de;
       border-radius: 10px;
       margin: 0.85em 0;
       background: #f6f8fa;
       box-shadow: 0 1px 2px rgba(27, 31, 36, 0.04);
   }
   .input-toggle summary {
       cursor: pointer;
       padding: 0.78em 1.0em;
       font-weight: 700;
       color: #24292f;
       background: linear-gradient(180deg, #f6f8fa 0%, #eef1f4 100%);
       border-radius: 10px;
       list-style-position: outside;
   }
   .input-toggle summary:hover {
       background: #eef1f4;
   }
   .input-toggle[open] summary {
       border-bottom: 1px solid #d0d7de;
       border-radius: 10px 10px 0 0;
   }
   .input-toggle-body {
       padding: 0;
       background: #ffffff;
       border-radius: 0 0 10px 10px;
   }
   .input-copy-row {
       display: flex;
       align-items: center;
       justify-content: space-between;
       gap: 0.75em;
       padding: 0.55em 0.75em;
       background: #f6f8fa;
       border-bottom: 1px solid #d0d7de;
   }
   .input-file-name {
       font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
       font-size: 0.86em;
       color: #57606a;
   }
   .copy-input-button {
       display: inline-flex;
       align-items: center;
       justify-content: center;
       gap: 0.32em;
       min-width: 4.9em;
       border: 1px solid #d0d7de;
       background: #f6f8fa;
       color: #24292f;
       border-radius: 6px;
       padding: 0.28em 0.62em;
       font-size: 0.80em;
       line-height: 1.25;
       font-weight: 600;
       cursor: pointer;
       box-shadow: inset 0 1px 0 rgba(255,255,255,0.65), 0 1px 0 rgba(27,31,36,0.04);
   }
   .copy-input-button::before {
       content: "⧉";
       font-size: 0.95em;
       color: #57606a;
   }
   .copy-input-button:hover {
       background: #eef1f4;
       border-color: #afb8c1;
   }
   .copy-input-button.copied {
       color: #1a7f37;
       border-color: #a6d9b6;
       background: #dafbe1;
   }
   .copy-input-button.copied::before {
       content: "✓";
       color: #1a7f37;
   }
   .input-code {
       display: block;
       margin: 0;
       max-height: 42rem;
       overflow-y: auto;
       overflow-x: auto;
       white-space: pre-wrap;
       overflow-wrap: anywhere;
       background: #f6f8fa;
       border: 0;
       border-radius: 0 0 10px 10px;
       padding: 1.0em;
       font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
       font-size: 0.84em;
       line-height: 1.45;
       color: #24292f;
       text-align: left;
       direction: ltr;
       tab-size: 2;
   }
   .input-code code {
       display: block;
       white-space: pre-wrap;
       overflow-wrap: anywhere;
   }
   </style>
   <script>
   window.copyInputBlock = window.copyInputBlock || function(id, button) {
       var el = document.getElementById(id);
       if (!el) return;
       var text = el.innerText || el.textContent || '';
       function showCopied() {
           var old = button.textContent;
           button.textContent = 'Copied';
           button.classList.add('copied');
           window.setTimeout(function() {
               button.textContent = old;
               button.classList.remove('copied');
           }, 1400);
       }
       function fallbackCopy() {
           var ta = document.createElement('textarea');
           ta.value = text;
           ta.setAttribute('readonly', '');
           ta.style.position = 'fixed';
           ta.style.left = '-9999px';
           document.body.appendChild(ta);
           ta.select();
           try { document.execCommand('copy'); showCopied(); } catch (err) { console.error(err); }
           document.body.removeChild(ta);
       }
       if (navigator.clipboard && window.isSecureContext) {
           navigator.clipboard.writeText(text).then(showCopied).catch(fallbackCopy);
       } else {
           fallbackCopy();
       }
   };
   </script>

OpenMX
~~~~~~

.. raw:: html

   <details class="input-toggle">
     <summary>立方晶 — OptC3</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">openmx.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('input-openmx-cubic', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="input-openmx-cubic" class="language-text">#
   #    File Name
   #

   System.CurrrentDirectory ./
   System.Name BTO_Cubic_latticeOnly_OptC3
   DATA.PATH /usr/local/rsdft/DFT_DATA19

   #
   # Definition of Atomic Species
   #

   Species.Number 3
   &lt;Definition.of.Atomic.Species
    Ba  Ba10.0-s3p2d2f1  Ba_PBE19
    Ti  Ti7.0-s3p2d2f1   Ti_PBE19
    O   O6.0-s3p2d2      O_PBE19
   Definition.of.Atomic.Species&gt;

   #
   # Atoms
   #
   Atoms.Number 5
   Atoms.SpeciesAndCoordinates.Unit FRAC
   &lt;Atoms.SpeciesAndCoordinates
    1 Ba 0.0 0.0 0.0 5.0 5.0
    2 Ti 0.5 0.5 0.5 6.0 6.0
    3 O 0.5 0.5 0.0 3.0 3.0
    4 O 0.5 0.0 0.5 3.0 3.0
    5 O 0.0 0.5 0.5 3.0 3.0
   Atoms.SpeciesAndCoordinates&gt;
   Atoms.UnitVectors.Unit Ang
   &lt;Atoms.UnitVectors
    4.0 0.0 2.4492935982947064e-16
    6.432490598706545e-16 4.0 2.4492935982947064e-16
    0.0 0.0 4.0
   Atoms.UnitVectors&gt;

   #
   # SCF / Electronic System
   #

   scf.XcType                 GGA-PBE
   scf.SpinPolarization       off
   scf.ElectronicTemperature  300.0
   scf.energycutoff           500
   scf.maxIter                500
   scf.EigenvalueSolver       band
   scf.Kgrid                  6 6 6
   scf.criterion              1.0e-8
   scf.system.charge          0.0

   scf.Mixing.Type            RMM-DIISK
   scf.Init.Mixing.Weight     0.20
   scf.Min.Mixing.Weight      0.001
   scf.Max.Mixing.Weight      0.40
   scf.Mixing.History         30
   scf.Mixing.StartPulay      6

   scf.Electric.Field         0.0 0.0 0.0

   #
   # Lattice-only variable-cell optimization
   # OptC3: fixed fractional coordinates, fixed cell angles, and constrained a = b = c.
   #

   MD.Type                    OptC3
   MD.maxIter                 500
   MD.Opt.criterion           1.0e-4
   MD.Opt.DIIS.History        3
   MD.Opt.StartDIIS           5
   MD.Opt.EveryDIIS           200
   MD.Opt.Init.Hessian        Schlegel
   MD.applied.pressure        0.0
   </code></pre>
     </div>
   </details>
   <details class="input-toggle">
     <summary>正方晶 — OptC4</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">openmx.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('input-openmx-tetragonal', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="input-openmx-tetragonal" class="language-text">#
   # File Name / System
   #

   System.CurrrentDirectory  ./
   System.Name               BTO_Tetragonal_paperDFT_OptC4
   DATA.PATH                 /usr/local/rsdft/DFT_DATA19

   #
   # Definition of Atomic Species
   # Larger PAO basis for phase-energy comparison
   #

   Species.Number 3
   &lt;Definition.of.Atomic.Species
    Ba  Ba10.0-s3p2d2f1  Ba_PBE19
    Ti  Ti7.0-s3p2d2f1   Ti_PBE19
    O   O6.0-s3p2d2      O_PBE19
   Definition.of.Atomic.Species&gt;

   #
   # Atoms
   # Tetragonal polar [001] seed; paper DFT a = 4.005 A and c/a = 1.047; OptC4 preserves a=b and fixed angles.
   #

   Atoms.Number 5
   Atoms.SpeciesAndCoordinates.Unit FRAC
   &lt;Atoms.SpeciesAndCoordinates
    1  Ba  0.000000000000  0.000000000000  0.000000000000   5.0  5.0
    2  Ti  0.500000000000  0.500000000000  0.520000000000   6.0  6.0
    3  O   0.500000000000  0.500000000000  0.985000000000   3.0  3.0
    4  O   0.500000000000  0.000000000000  0.485000000000   3.0  3.0
    5  O   0.000000000000  0.500000000000  0.485000000000   3.0  3.0
   Atoms.SpeciesAndCoordinates&gt;

   Atoms.UnitVectors.Unit Ang
   &lt;Atoms.UnitVectors
        4.005000000000     0.000000000000     0.000000000000
        0.000000000000     4.005000000000     0.000000000000
        0.000000000000     0.000000000000     4.193235000000
   Atoms.UnitVectors&gt;

   #
   # SCF / Electronic System
   #

   scf.XcType                 GGA-PBE
   scf.SpinPolarization       off
   scf.ElectronicTemperature  300.0
   scf.energycutoff           500
   scf.maxIter                500
   scf.EigenvalueSolver       band
   scf.Kgrid                  6 6 6
   scf.criterion              1.0e-8
   scf.system.charge          0.0

   scf.Mixing.Type            RMM-DIISK
   scf.Init.Mixing.Weight     0.20
   scf.Min.Mixing.Weight      0.001
   scf.Max.Mixing.Weight      0.40
   scf.Mixing.History         30
   scf.Mixing.StartPulay      6

   scf.Electric.Field         0.0 0.0 0.0

   #
   # Phase-preserving lattice-only optimization
   # Fractional atomic coordinates are fixed in OptC modes.
   #

   MD.Type                    OptC4
   MD.maxIter                 500
   MD.Opt.criterion           1.0e-4
   MD.Opt.DIIS.History        3
   MD.Opt.StartDIIS           5
   MD.Opt.EveryDIIS           200
   MD.Opt.Init.Hessian        Schlegel
   MD.applied.pressure        0.0
   </code></pre>
     </div>
   </details>
   <details class="input-toggle">
     <summary>斜方晶 — OptC2</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">openmx.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('input-openmx-orthorhombic', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="input-openmx-orthorhombic" class="language-text">#
   # File Name / System
   #

   System.CurrrentDirectory  ./
   System.Name               BTO_Orthorhombic_paperDFT_OptC2
   DATA.PATH                 /usr/local/rsdft/DFT_DATA19

   #
   # Definition of Atomic Species
   # Larger PAO basis for phase-energy comparison
   #

   Species.Number 3
   &lt;Definition.of.Atomic.Species
    Ba  Ba10.0-s3p2d2f1  Ba_PBE19
    Ti  Ti7.0-s3p2d2f1   Ti_PBE19
    O   O6.0-s3p2d2      O_PBE19
   Definition.of.Atomic.Species&gt;

   #
   # Atoms
   # Orthorhombic polar [110] seed; paper DFT a=3.995 A, b=5.800 A, c=5.841 A; OptC2 preserves 90 degree angles.
   #

   Atoms.Number 10
   Atoms.SpeciesAndCoordinates.Unit FRAC
   &lt;Atoms.SpeciesAndCoordinates
    1   Ba  0.000000000000  0.000000000000  0.000000000000   5.0  5.0
    2   Ba  0.000000000000  0.500000000000  0.500000000000   5.0  5.0
    3   Ti  0.503000000000  0.003000000000  0.500000000000   6.0  6.0
    4   Ti  0.503000000000  0.503000000000  0.000000000000   6.0  6.0
    5   O   0.498500000000  0.248500000000  0.250000000000   3.0  3.0
    6   O   0.498500000000  0.748500000000  0.750000000000   3.0  3.0
    7   O   0.498500000000  0.248500000000  0.750000000000   3.0  3.0
    8   O   0.498500000000  0.748500000000  0.250000000000   3.0  3.0
    9   O   0.998500000000  0.998500000000  0.500000000000   3.0  3.0
    10  O   0.998500000000  0.498500000000  0.000000000000   3.0  3.0
   Atoms.SpeciesAndCoordinates&gt;

   Atoms.UnitVectors.Unit Ang
   &lt;Atoms.UnitVectors
        3.995000000000     0.000000000000     0.000000000000
        0.000000000000     5.800000000000     0.000000000000
        0.000000000000     0.000000000000     5.841000000000
   Atoms.UnitVectors&gt;

   #
   # SCF / Electronic System
   #

   scf.XcType                 GGA-PBE
   scf.SpinPolarization       off
   scf.ElectronicTemperature  300.0
   scf.energycutoff           500
   scf.maxIter                500
   scf.EigenvalueSolver       band
   scf.Kgrid                  6 4 4
   scf.criterion              1.0e-8
   scf.system.charge          0.0

   scf.Mixing.Type            RMM-DIISK
   scf.Init.Mixing.Weight     0.20
   scf.Min.Mixing.Weight      0.001
   scf.Max.Mixing.Weight      0.40
   scf.Mixing.History         30
   scf.Mixing.StartPulay      6

   scf.Electric.Field         0.0 0.0 0.0

   #
   # Phase-preserving lattice-only optimization
   # Fractional atomic coordinates are fixed in OptC modes.
   #

   MD.Type                    OptC2
   MD.maxIter                 500
   MD.Opt.criterion           1.0e-4
   MD.Opt.DIIS.History        3
   MD.Opt.StartDIIS           5
   MD.Opt.EveryDIIS           200
   MD.Opt.Init.Hessian        Schlegel
   MD.applied.pressure        0.0
   </code></pre>
     </div>
   </details>
   <details class="input-toggle">
     <summary>菱面体晶 — OptC3</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">openmx.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('input-openmx-rhombohedral', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="input-openmx-rhombohedral" class="language-text">#
   # File Name / System
   #

   System.CurrrentDirectory  ./
   System.Name               BTO_Rhombohedral_paperDFT_OptC3
   DATA.PATH                 /usr/local/rsdft/DFT_DATA19

   #
   # Definition of Atomic Species
   # Larger PAO basis for phase-energy comparison
   #

   Species.Number 3
   &lt;Definition.of.Atomic.Species
    Ba  Ba10.0-s3p2d2f1  Ba_PBE19
    Ti  Ti7.0-s3p2d2f1   Ti_PBE19
    O   O6.0-s3p2d2      O_PBE19
   Definition.of.Atomic.Species&gt;

   #
   # Atoms
   # Rhombohedral polar [111] seed; paper DFT a = 4.072 A and alpha = beta = gamma = 89.757 deg; OptC3 preserves equal lengths and fixed angles.
   #

   Atoms.Number 5
   Atoms.SpeciesAndCoordinates.Unit FRAC
   &lt;Atoms.SpeciesAndCoordinates
    1  Ba  0.000000000000  0.000000000000  0.000000000000   5.0  5.0
    2  Ti  0.515000000000  0.515000000000  0.515000000000   6.0  6.0
    3  O   0.485000000000  0.485000000000  0.000000000000   3.0  3.0
    4  O   0.485000000000  0.000000000000  0.485000000000   3.0  3.0
    5  O   0.000000000000  0.485000000000  0.485000000000   3.0  3.0
   Atoms.SpeciesAndCoordinates&gt;

   Atoms.UnitVectors.Unit Ang
   &lt;Atoms.UnitVectors
        4.072000000000     0.000000000000     0.000000000000
        0.017269911362     4.071963377802     0.000000000000
        0.017269911362     0.017196821958     4.071927064607
   Atoms.UnitVectors&gt;

   #
   # SCF / Electronic System
   #

   scf.XcType                 GGA-PBE
   scf.SpinPolarization       off
   scf.ElectronicTemperature  300.0
   scf.energycutoff           500
   scf.maxIter                500
   scf.EigenvalueSolver       band
   scf.Kgrid                  6 6 6
   scf.criterion              1.0e-8
   scf.system.charge          0.0

   scf.Mixing.Type            RMM-DIISK
   scf.Init.Mixing.Weight     0.20
   scf.Min.Mixing.Weight      0.001
   scf.Max.Mixing.Weight      0.40
   scf.Mixing.History         30
   scf.Mixing.StartPulay      6

   scf.Electric.Field         0.0 0.0 0.0

   #
   # Phase-preserving lattice-only optimization
   # Fractional atomic coordinates are fixed in OptC modes.
   #

   MD.Type                    OptC3
   MD.maxIter                 500
   MD.Opt.criterion           1.0e-4
   MD.Opt.DIIS.History        3
   MD.Opt.StartDIIS           5
   MD.Opt.EveryDIIS           200
   MD.Opt.Init.Hessian        Schlegel
   MD.applied.pressure        0.0
   </code></pre>
     </div>
   </details>

QE
~~

.. raw:: html

   <details class="input-toggle">
     <summary>立方晶 — ibrav=1</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">QuloudJob.scf.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('input-qe-cubic', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="input-qe-cubic" class="language-fortran">&amp;control
     calculation    = &#x27;vc-relax&#x27;
     prefix         = &#x27;QuloudJob&#x27;
     pseudo_dir     = &#x27;./&#x27;
     outdir         = &#x27;./work&#x27;
     verbosity      = &#x27;high&#x27;
     tstress        = .true.
     tprnfor        = .true.
     etot_conv_thr  = 1.0d-5
     forc_conv_thr  = 1.0d-4
     nstep          = 100
   /
   &amp;system
     ibrav       = 1
     A           = 4.006
     nat         = 5
     ntyp        = 3
     ecutwfc     = 52.0
     ecutrho     = 575.0
     input_dft   = &#x27;PBE&#x27;
     tot_charge  = 0.0
     occupations = &#x27;fixed&#x27;
     nspin       = 1
   /
   &amp;electrons
     conv_thr         = 1.0d-10
     mixing_beta      = 0.7
     electron_maxstep = 100
   /
   &amp;ions
     ion_dynamics = &#x27;bfgs&#x27;
   /
   &amp;cell
     cell_dynamics  = &#x27;bfgs&#x27;
     cell_dofree    = &#x27;ibrav&#x27;
     press          = 0.0
     press_conv_thr = 0.5
   /
   ATOMIC_SPECIES
   Ba 137.327 Ba.pbe-spn-rrkjus_psl.1.0.0.UPF
   Ti  47.867 Ti.pbe-spn-rrkjus_psl.1.0.0.UPF
   O   15.999 O.pbe-nl-rrkjus_psl.1.0.0.UPF

   ATOMIC_POSITIONS {crystal}
   Ba 0.0 0.0 0.0 0 0 0
   Ti 0.5 0.5 0.5 0 0 0
   O  0.5 0.5 0.0 0 0 0
   O  0.5 0.0 0.5 0 0 0
   O  0.0 0.5 0.5 0 0 0

   K_POINTS {automatic}
   6 6 6 0 0 0
   </code></pre>
     </div>
   </details>
   <details class="input-toggle">
     <summary>正方晶 — ibrav=6</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">QuloudJob.scf.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('input-qe-tetragonal', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="input-qe-tetragonal" class="language-fortran">&amp;control
     calculation    = &#x27;vc-relax&#x27;
     prefix         = &#x27;BTO_tetragonal_latticeOnly&#x27;
     pseudo_dir     = &#x27;./&#x27;
     outdir         = &#x27;./work&#x27;
     verbosity      = &#x27;high&#x27;
     tstress        = .true.
     tprnfor        = .true.
     etot_conv_thr  = 1.0d-5
     forc_conv_thr  = 1.0d-4
     nstep          = 100
   /
   &amp;system
     ibrav       = 6
     A           = 3.9940000000
     C           = 4.0340000000
     nat         = 5
     ntyp        = 3
     ecutwfc     = 52.0
     ecutrho     = 575.0
     input_dft   = &#x27;PBE&#x27;
     tot_charge  = 0.0
     occupations = &#x27;fixed&#x27;
     nspin       = 1
   /
   &amp;electrons
     conv_thr         = 1.0d-10
     mixing_beta      = 0.7
     electron_maxstep = 100
   /
   &amp;ions
     ion_dynamics = &#x27;bfgs&#x27;
   /
   &amp;cell
     cell_dynamics  = &#x27;bfgs&#x27;
     cell_dofree    = &#x27;ibrav&#x27;
     press          = 0.0
     press_conv_thr = 0.5
   /
   ATOMIC_SPECIES
   Ba 137.327 Ba.pbe-spn-rrkjus_psl.1.0.0.UPF
   Ti  47.867 Ti.pbe-spn-rrkjus_psl.1.0.0.UPF
   O   15.999 O.pbe-nl-rrkjus_psl.1.0.0.UPF

   ATOMIC_POSITIONS {crystal}
   Ba  0.000000000000  0.000000000000  0.000000000000 0 0 0
   Ti  0.499983187328  0.499983187328  0.519965796714 0 0 0
   O   0.499983187328  0.499983187328  0.984935211083 0 0 0
   O   0.499983187328  0.000000000000  0.484968098858 0 0 0
   O   0.000000000000  0.499983187328  0.484968098858 0 0 0

   K_POINTS {automatic}
   6 6 6 0 0 0
   </code></pre>
     </div>
   </details>
   <details class="input-toggle">
     <summary>斜方晶 — ibrav=8</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">QuloudJob.scf.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('input-qe-orthorhombic', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="input-qe-orthorhombic" class="language-fortran">&amp;control
     calculation    = &#x27;vc-relax&#x27;
     prefix         = &#x27;BTO_orthorhombic_latticeOnly&#x27;
     pseudo_dir     = &#x27;./&#x27;
     outdir         = &#x27;./work&#x27;
     verbosity      = &#x27;high&#x27;
     tstress        = .true.
     tprnfor        = .true.
     etot_conv_thr  = 1.0d-5
     forc_conv_thr  = 1.0d-4
     nstep          = 100
   /
   &amp;system
     ibrav       = 8
     A           = 3.9920000000
     B           = 5.6750000000
     C           = 5.6820000000
     nat         = 10
     ntyp        = 3
     ecutwfc     = 52.0
     ecutrho     = 575.0
     input_dft   = &#x27;PBE&#x27;
     tot_charge  = 0.0
     occupations = &#x27;fixed&#x27;
     nspin       = 1
   /
   &amp;electrons
     conv_thr         = 1.0d-10
     mixing_beta      = 0.7
     electron_maxstep = 100
   /
   &amp;ions
     ion_dynamics = &#x27;bfgs&#x27;
   /
   &amp;cell
     cell_dynamics  = &#x27;bfgs&#x27;
     cell_dofree    = &#x27;ibrav&#x27;
     press          = 0.0
     press_conv_thr = 0.5
   /
   ATOMIC_SPECIES
   Ba 137.327 Ba.pbe-spn-rrkjus_psl.1.0.0.UPF
   Ti  47.867 Ti.pbe-spn-rrkjus_psl.1.0.0.UPF
   O   15.999 O.pbe-nl-rrkjus_psl.1.0.0.UPF

   ATOMIC_POSITIONS {crystal}
   Ba  0.000000000000  0.000000000000  0.000000000000 0 0 0
   Ba  0.000000000000  0.500008826693  0.500006672387 0 0 0
   Ti  0.502938513464  0.003000052960  0.500006672387 0 0 0
   Ti  0.502938513464  0.503008879654  0.000000000000 0 0 0
   O   0.498439063542  0.248504386867  0.250003336194 0 0 0
   O   0.498439063542  0.748513213560  0.750010008581 0 0 0
   O   0.498439063542  0.248504386867  0.750010008581 0 0 0
   O   0.498439063542  0.748513213560  0.250003336194 0 0 0
   O   0.998377943725  0.998517626907  0.500006672387 0 0 0
   O   0.998377943725  0.498508800213  0.000000000000 0 0 0

   K_POINTS {automatic}
   6 4 4 0 0 0
   </code></pre>
     </div>
   </details>
   <details class="input-toggle">
     <summary>菱面体晶 — ibrav=5</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">QuloudJob.scf.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('input-qe-rhombohedral', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="input-qe-rhombohedral" class="language-fortran">&amp;control
     calculation    = &#x27;vc-relax&#x27;
     prefix         = &#x27;BTO_rhombohedral_latticeOnly&#x27;
     pseudo_dir     = &#x27;./&#x27;
     outdir         = &#x27;./work&#x27;
     verbosity      = &#x27;high&#x27;
     tstress        = .true.
     tprnfor        = .true.
     etot_conv_thr  = 1.0d-5
     forc_conv_thr  = 1.0d-4
     nstep          = 100
   /
   &amp;system
     ibrav       = 5
     A           = 4.0010000000
     cosAB       = 0.002617990887
     nat         = 5
     ntyp        = 3
     ecutwfc     = 52.0
     ecutrho     = 575.0
     input_dft   = &#x27;PBE&#x27;
     tot_charge  = 0.0
     occupations = &#x27;fixed&#x27;
     nspin       = 1
   /
   &amp;electrons
     conv_thr         = 1.0d-10
     mixing_beta      = 0.7
     electron_maxstep = 100
   /
   &amp;ions
     ion_dynamics = &#x27;bfgs&#x27;
   /
   &amp;cell
     cell_dynamics  = &#x27;bfgs&#x27;
     cell_dofree    = &#x27;ibrav&#x27;
     press          = 0.0
     press_conv_thr = 0.5
   /
   ATOMIC_SPECIES
   Ba 137.327 Ba.pbe-spn-rrkjus_psl.1.0.0.UPF
   Ti  47.867 Ti.pbe-spn-rrkjus_psl.1.0.0.UPF
   O   15.999 O.pbe-nl-rrkjus_psl.1.0.0.UPF

   ATOMIC_POSITIONS {crystal}
   Ba  0.000000000000  0.000000000000  0.000000000000 0 0 0
   Ti  0.515099343387  0.515099343387  0.515099343387 0 0 0
   O   0.485093556394  0.485093556394  0.000000000000 0 0 0
   O   0.485093556394  0.000000000000  0.485093556394 0 0 0
   O   0.000000000000  0.485093556394  0.485093556394 0 0 0

   K_POINTS {automatic}
   6 6 6 0 0 0
   </code></pre>
     </div>
   </details>


MLIP
~~~~

以下の例は、QuloudのASEまたはLAMMPSジョブでセルを含む緩和を行うための最小設定である。ASEでは ``ase.in``、LAMMPSでは ``in.QuloudJob`` を置き換えて使う。構造データは各相のジョブに含まれるものを利用するため、同じ形式の入力を各相に適用できる。

.. list-table:: MLIP入力の対応
   :header-rows: 1
   :widths: 24 26 50

   * - 手法
     - ファイル
     - セル緩和の指定
   * - ASE SevenNet
     - ``ase.in``
     - ``latopt: true``
   * - ASE FairChem
     - ``ase.in``
     - ``latopt: true``
   * - LAMMPS CHGNet
     - ``in.QuloudJob``
     - ``fix box/relax aniso``

.. raw:: html

   <details class="input-toggle">
     <summary>ASE SevenNet — lattice optimization</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">ase.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('input-mlip-sevennet', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="input-mlip-sevennet" class="language-text">{
     &quot;mode&quot;: &quot;opt&quot;,
     &quot;opt&quot;: {
       &quot;fmax&quot;: 0.01,
       &quot;ntime&quot;: 100,
       &quot;latopt&quot;: true
     },
     &quot;provider&quot;: &quot;7net&quot;,
     &quot;model_name&quot;: &quot;7net-mf-ompa&quot;
   }</code></pre>
     </div>
   </details>
   <details class="input-toggle">
     <summary>ASE FairChem — lattice optimization</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">ase.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('input-mlip-fairchem', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="input-mlip-fairchem" class="language-text">{
     &quot;mode&quot;: &quot;opt&quot;,
     &quot;opt&quot;: {
       &quot;fmax&quot;: 0.01,
       &quot;ntime&quot;: 100,
       &quot;latopt&quot;: true
     },
     &quot;provider&quot;: &quot;fairchem&quot;,
     &quot;model_name&quot;: &quot;uma-s-1p1&quot;
   }</code></pre>
     </div>
   </details>
   <details class="input-toggle">
     <summary>LAMMPS CHGNet — lattice optimization</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">in.QuloudJob</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('input-mlip-chgnet-lammps', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="input-mlip-chgnet-lammps" class="language-text">#Generated by Quloud
   units metal
   boundary p p p
   atom_style atomic
   read_data QuloudJob.lmp
   replicate 1 1 1
   pair_style chgnet ../../../../../../../../CHGNET
   pair_coeff * * 0.3.0 Ba Ti O
   thermo_style custom step etotal temp density vol press
   thermo 10
   dump 1 all atom 5 QuloudJob.lammpstrj
   fix 1 all box/relax aniso 0.0 vmax 0.001
   minimize 1.0e-15 1.0e-7 1000 10000
   write_data QuloudJob.out.lmp
   </code></pre>
     </div>
   </details>

格子定数の実験値および計算値
----------------------------

.. raw:: html

   <div class="table-scroll">
   <table class="slide-style-table table-lattice">
     <colgroup>
       <col style="width: 8%;">
       <col style="width: 8%;">
       <col style="width: 8%;">
       <col style="width: 7%;">
       <col style="width: 8%;">
       <col style="width: 7%;">
       <col style="width: 7%;">
       <col style="width: 7%;">
       <col style="width: 7%;">
       <col style="width: 7%;">
       <col style="width: 10%;">
       <col style="width: 8%;">
       <col style="width: 8%;">
     </colgroup>
     <caption>BaTiO₃の格子定数の比較</caption>
     <thead>
       <tr>
         <th rowspan="2">相</th>
         <th rowspan="2">最適化法<br>（OpenMX）</th>
         <th rowspan="2">最適化法<br>（QE）</th>
         <th rowspan="2">格子定数</th>
         <th rowspan="2">実験値 <sup>[1,2]</sup></th>
         <th class="group-header" colspan="2">DFT法</th>
         <th class="group-header" colspan="3">MLIP法</th>
         <th class="group-header" colspan="3">先行研究</th>
       </tr>
       <tr>
         <th>OpenMX</th>
         <th>QE</th>
         <th>CHGNet</th>
         <th>SevenNet</th>
         <th>FairChem</th>
         <th>文献 DFT</th>
         <th>文献 MD</th>
         <th>文献 ACE</th>
       </tr>
     </thead>
     <tbody>
       <tr>
         <td class="phase-cell">立方晶</td>
         <td class="method-cell">Optc3</td>
         <td class="method-cell">ibrav=1</td>
         <td class="parameter-cell">a (Å)</td>
         <td class="value-cell">4.006</td>
         <td class="value-cell">4.020</td>
         <td class="value-cell">4.024</td>
         <td class="value-cell">4.036</td>
         <td class="value-cell">4.035</td>
         <td class="value-cell">4.035</td>
         <td class="value-cell ref-cell"><div class="ref-subrow">4.035 <sup>[3]</sup></div><div class="ref-subrow">4.002 <sup>[4]</sup></div></td>
         <td class="value-cell">4.037 <sup>[4]</sup></td>
         <td class="value-cell">4.039 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="phase-cell" rowspan="2">正方晶</td>
         <td class="method-cell" rowspan="2">Optc4</td>
         <td class="method-cell" rowspan="2">ibrav=6</td>
         <td class="parameter-cell">a (Å)</td>
         <td class="value-cell">3.994</td>
         <td class="value-cell">4.012</td>
         <td class="value-cell">4.015</td>
         <td class="value-cell">4.002</td>
         <td class="value-cell">4.012</td>
         <td class="value-cell">4.009</td>
         <td class="value-cell ref-cell"><div class="ref-subrow">4.005 <sup>[3]</sup></div><div class="ref-subrow">3.985 <sup>[4]</sup></div></td>
         <td class="value-cell">4.005 <sup>[4]</sup></td>
         <td class="value-cell">4.011 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="parameter-cell">c/a</td>
         <td class="value-cell">1.010</td>
         <td class="value-cell">1.013</td>
         <td class="value-cell">1.013</td>
         <td class="value-cell">1.050</td>
         <td class="value-cell">1.041</td>
         <td class="value-cell">1.042</td>
         <td class="value-cell ref-cell"><div class="ref-subrow">1.047 <sup>[3]</sup></div><div class="ref-subrow">1.026 <sup>[4]</sup></div></td>
         <td class="value-cell">1.026 <sup>[4]</sup></td>
         <td class="value-cell">1.045 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="phase-cell" rowspan="3">斜方晶</td>
         <td class="method-cell" rowspan="3">Optc2</td>
         <td class="method-cell" rowspan="3">ibrav=8</td>
         <td class="parameter-cell">a (Å)</td>
         <td class="value-cell">3.992</td>
         <td class="value-cell">4.019</td>
         <td class="value-cell">4.025</td>
         <td class="value-cell">4.075</td>
         <td class="value-cell">4.039</td>
         <td class="value-cell">4.035</td>
         <td class="value-cell ref-cell"><div class="ref-subrow">3.995 <sup>[3]</sup></div><div class="ref-subrow">3.977 <sup>[4]</sup></div></td>
         <td class="value-cell">3.997 <sup>[4]</sup></td>
         <td class="value-cell">3.989 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="parameter-cell">b (Å)</td>
         <td class="value-cell">5.675</td>
         <td class="value-cell">5.687</td>
         <td class="value-cell">5.693</td>
         <td class="value-cell">5.777</td>
         <td class="value-cell">5.800</td>
         <td class="value-cell">5.797</td>
         <td class="value-cell ref-cell"><div class="ref-subrow">5.800 <sup>[3]</sup></div><div class="ref-subrow">5.722 <sup>[4]</sup></div></td>
         <td class="value-cell">5.740 <sup>[4]</sup></td>
         <td class="value-cell">5.812 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="parameter-cell">c (Å)</td>
         <td class="value-cell">5.682</td>
         <td class="value-cell">5.686</td>
         <td class="value-cell">5.691</td>
         <td class="value-cell">5.750</td>
         <td class="value-cell">5.780</td>
         <td class="value-cell">5.779</td>
         <td class="value-cell ref-cell"><div class="ref-subrow">5.841 <sup>[3]</sup></div><div class="ref-subrow">5.722 <sup>[4]</sup></div></td>
         <td class="value-cell">5.740 <sup>[4]</sup></td>
         <td class="value-cell">5.844 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="phase-cell" rowspan="2">菱面体晶</td>
         <td class="method-cell" rowspan="2">Optc3</td>
         <td class="method-cell" rowspan="2">ibrav=5</td>
         <td class="parameter-cell">a (Å)</td>
         <td class="value-cell">4.001</td>
         <td class="value-cell">4.023</td>
         <td class="value-cell">4.027</td>
         <td class="value-cell">4.077</td>
         <td class="value-cell">4.076</td>
         <td class="value-cell">4.076</td>
         <td class="value-cell ref-cell"><div class="ref-subrow">4.072 <sup>[3]</sup></div><div class="ref-subrow">4.024 <sup>[4]</sup></div></td>
         <td class="value-cell">4.036 <sup>[4]</sup></td>
         <td class="value-cell">4.077 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="parameter-cell">α=β=γ (°)</td>
         <td class="value-cell">89.85</td>
         <td class="value-cell">89.76</td>
         <td class="value-cell">89.75</td>
         <td class="value-cell">89.76</td>
         <td class="value-cell">89.66</td>
         <td class="value-cell">89.66</td>
         <td class="value-cell ref-cell"><div class="ref-subrow">89.76 <sup>[3]</sup></div><div class="ref-subrow">—</div></td>
         <td class="value-cell">—</td>
         <td class="value-cell">89.76 <sup>[3]</sup></td>
       </tr>
     </tbody>
   </table>
   </div>

実験値欄では、立方晶相、正方晶相、菱面体晶相についてKweiら :sup:`[1]`、斜方晶相についてShiraneら :sup:`[2]` の値を参照した。
文献DFTおよび文献ACEのうち、Sehrawatら :sup:`[3]` の値は同文献に報告されたDFT参照計算およびACEポテンシャルによる計算結果である。
Qiら :sup:`[4]` の文献MDおよび文献DFTの値は、同文献に報告されたMDおよびDFTの格子定数である。正方晶相の :math:`c/a` は文献中の :math:`a` および :math:`c` から算出した。また、Qiら :sup:`[4]` の斜方晶相の :math:`b=c` は擬立方格子定数として示されているため、本表では現行の斜方晶セル表記に合わせて :math:`\sqrt{2}` 倍した値を掲載した。菱面体晶相の角度は同表に示されていないため、該当欄はダッシュで示した。
CHGNetの菱面体晶相の :math:`a` は、最適化後の :math:`a`、:math:`b`、:math:`c` の平均値として示した。
QEの値は、立方晶相、正方晶相、斜方晶相、菱面体晶相について、それぞれ ``ibrav=1``、``ibrav=6``、``ibrav=8``、``ibrav=5`` のBravais格子制約を保持した可変セル最適化結果である。
表中では、OpenMXおよびQEをDFT法、CHGNet、SevenNetおよびFairChemをMLIP法、文献DFT、文献MDおよび文献ACEを先行研究として分類した。
文献DFT欄では、上段にSehrawatら :sup:`[3]` の値、下段にQiら :sup:`[4]` の値を示した。

実験値に対する相対誤差
----------------------

相対誤差は次式により評価した。

.. math::

   \mathrm{Relative\ error} =
   \frac{|x_{\mathrm{calc}} - x_{\mathrm{exp}}|}{x_{\mathrm{exp}}}
   \times 100

ここで、:math:`x_{\mathrm{calc}}` は計算値、:math:`x_{\mathrm{exp}}` は実験値を表す。

.. raw:: html

   <div class="table-scroll">
   <table class="slide-style-table table-error">
     <colgroup>
       <col style="width: 9%;">
       <col style="width: 8%;">
       <col style="width: 8%;">
       <col style="width: 7%;">
       <col style="width: 7%;">
       <col style="width: 7%;">
       <col style="width: 7%;">
       <col style="width: 7%;">
       <col style="width: 7%;">
       <col style="width: 12%;">
       <col style="width: 9%;">
       <col style="width: 12%;">
     </colgroup>
     <caption>実験値に対する相対誤差（%）</caption>
     <thead>
       <tr>
         <th rowspan="2">相</th>
         <th rowspan="2">最適化法<br>（OpenMX）</th>
         <th rowspan="2">最適化法<br>（QE）</th>
         <th rowspan="2">格子定数</th>
         <th class="group-header" colspan="2">DFT法</th>
         <th class="group-header" colspan="3">MLIP法</th>
         <th class="group-header" colspan="3">先行研究</th>
       </tr>
       <tr>
         <th>OpenMX</th>
         <th>QE</th>
         <th>CHGNet</th>
         <th>SevenNet</th>
         <th>FairChem</th>
         <th>文献 DFT</th>
         <th>文献 MD</th>
         <th>文献 ACE</th>
       </tr>
     </thead>
     <tbody>
       <tr>
         <td class="phase-cell">立方晶</td>
         <td class="method-cell">Optc3</td>
         <td class="method-cell">ibrav=1</td>
         <td class="parameter-cell">a</td>
         <td class="err-green">0.35</td>
         <td class="err-green">0.46</td>
         <td class="err-yellow">0.75</td>
         <td class="err-yellow">0.72</td>
         <td class="err-yellow">0.72</td>
         <td class="error-multi"><div class="err-subrow err-yellow">0.72 <sup>[3]</sup></div><div class="err-subrow err-green">0.10 <sup>[4]</sup></div></td>
         <td class="err-yellow">0.77 <sup>[4]</sup></td>
         <td class="err-yellow">0.82 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="phase-cell" rowspan="2">正方晶</td>
         <td class="method-cell" rowspan="2">Optc4</td>
         <td class="method-cell" rowspan="2">ibrav=6</td>
         <td class="parameter-cell">a</td>
         <td class="err-green">0.45</td>
         <td class="err-yellow">0.53</td>
         <td class="err-green">0.19</td>
         <td class="err-green">0.45</td>
         <td class="err-green">0.38</td>
         <td class="error-multi"><div class="err-subrow err-green">0.28 <sup>[3]</sup></div><div class="err-subrow err-green">0.23 <sup>[4]</sup></div></td>
         <td class="err-green">0.28 <sup>[4]</sup></td>
         <td class="err-green">0.43 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="parameter-cell">c/a</td>
         <td class="err-green">0.30</td>
         <td class="err-green">0.31</td>
         <td class="err-red">3.92</td>
         <td class="err-red">3.07</td>
         <td class="err-red">3.17</td>
         <td class="error-multi"><div class="err-subrow err-red">3.66 <sup>[3]</sup></div><div class="err-subrow err-orange">1.59 <sup>[4]</sup></div></td>
         <td class="err-orange">1.58 <sup>[4]</sup></td>
         <td class="err-red">3.47 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="phase-cell" rowspan="3">斜方晶</td>
         <td class="method-cell" rowspan="3">Optc2</td>
         <td class="method-cell" rowspan="3">ibrav=8</td>
         <td class="parameter-cell">a</td>
         <td class="err-yellow">0.68</td>
         <td class="err-yellow">0.82</td>
         <td class="err-red">2.09</td>
         <td class="err-orange">1.18</td>
         <td class="err-orange">1.08</td>
         <td class="error-multi"><div class="err-subrow err-green">0.08 <sup>[3]</sup></div><div class="err-subrow err-green">0.38 <sup>[4]</sup></div></td>
         <td class="err-green">0.13 <sup>[4]</sup></td>
         <td class="err-green">0.08 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="parameter-cell">b</td>
         <td class="err-green">0.21</td>
         <td class="err-green">0.31</td>
         <td class="err-orange">1.80</td>
         <td class="err-red">2.20</td>
         <td class="err-red">2.15</td>
         <td class="error-multi"><div class="err-subrow err-red">2.20 <sup>[3]</sup></div><div class="err-subrow err-yellow">0.83 <sup>[4]</sup></div></td>
         <td class="err-orange">1.15 <sup>[4]</sup></td>
         <td class="err-red">2.41 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="parameter-cell">c</td>
         <td class="err-green">0.07</td>
         <td class="err-green">0.17</td>
         <td class="err-orange">1.19</td>
         <td class="err-orange">1.72</td>
         <td class="err-orange">1.71</td>
         <td class="error-multi"><div class="err-subrow err-red">2.80 <sup>[3]</sup></div><div class="err-subrow err-yellow">0.70 <sup>[4]</sup></div></td>
         <td class="err-orange">1.03 <sup>[4]</sup></td>
         <td class="err-red">2.85 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="phase-cell" rowspan="2">菱面体晶</td>
         <td class="method-cell" rowspan="2">Optc3</td>
         <td class="method-cell" rowspan="2">ibrav=5</td>
         <td class="parameter-cell">a</td>
         <td class="err-yellow">0.55</td>
         <td class="err-yellow">0.64</td>
         <td class="err-orange">1.90</td>
         <td class="err-orange">1.87</td>
         <td class="err-orange">1.87</td>
         <td class="error-multi"><div class="err-subrow err-orange">1.77 <sup>[3]</sup></div><div class="err-subrow err-yellow">0.57 <sup>[4]</sup></div></td>
         <td class="err-yellow">0.87 <sup>[4]</sup></td>
         <td class="err-orange">1.90 <sup>[3]</sup></td>
       </tr>
       <tr>
         <td class="parameter-cell">α</td>
         <td class="err-green">0.10</td>
         <td class="err-green">0.11</td>
         <td class="err-green">0.10</td>
         <td class="err-green">0.21</td>
         <td class="err-green">0.21</td>
         <td class="error-multi"><div class="err-subrow err-green">0.10 <sup>[3]</sup></div><div class="err-subrow">—</div></td>
         <td class="value-cell">—</td>
         <td class="err-green">0.10 <sup>[3]</sup></td>
       </tr>
     </tbody>
   </table>
   </div>

   <p>色は実験値に対する相対誤差の大きさを示す。緑は0.5%未満、黄は0.5–1.0%、橙は1.0–2.0%、赤は2.0%超を表す。</p>
   <div class="color-guide-title">表 1.2 相対誤差の色分け基準</div>
   <table class="color-guide-horizontal">
     <tbody>
       <tr>
         <td class="err-green">緑<br>&lt; 0.5%</td>
         <td class="err-yellow">黄<br>0.5–1.0%</td>
         <td class="err-orange">橙<br>1.0–2.0%</td>
         <td class="err-red">赤<br>&gt; 2.0%</td>
       </tr>
     </tbody>
   </table>

結果の概要
----------

本比較では、DFT計算だけでなくMLIPを用いた計算でも、実験値に近いBaTiO₃の格子定数が得られることが確認できた。実験値に対する全8項目の平均相対誤差で見ると、OpenMXは約0.34%、QEは約0.42%であり、いずれも1%を大きく下回った。これは、今回用いた相ごとの格子拘束と内部座標固定の設定により、立方晶、正方晶、斜方晶、菱面体晶の格子の特徴を保ったまま、安定な格子定数を評価できたことを示している。

先行計算との比較でも、本結果は良好である。Sehrawatらの文献DFT :sup:`[3]` の平均相対誤差は約1.45%、文献ACE :sup:`[3]` は約1.51%であった。Qiら :sup:`[4]` の文献DFTおよび文献MDは菱面体晶相の角度が報告されていないため7項目での比較となるが、それぞれ約0.63%および約0.83%であった。したがって、本研究で得られたOpenMXおよびQEの格子定数は、実験値だけでなく既報のDFT/MD/ACE計算とも十分に比較可能な精度にある。

MLIPについても、FairChem、SevenNet、CHGNetの平均相対誤差はおおむね約1.4--1.5%の範囲に収まった。これはOpenMXやQEよりはやや大きいものの、Sehrawatらの文献DFTおよびACEと同程度である。特に、これらのMLIPは計算コストが小さいにもかかわらず、立方晶では非極性構造、正方晶では :math:`[001]` 型、斜方晶では :math:`[110]` 型、菱面体晶では :math:`[111]` 型の強誘電的な格子・変位の特徴を保つことができた。したがって、MLIPは高精度DFTの代替ではなく、相ごとの構造探索や初期スクリーニングに有効な手法として位置づけられる。

項目ごとに見ると、OpenMXおよびQEでは、立方晶相の :math:`a` や菱面体晶相の角度 :math:`\alpha` などで実験値との差が特に小さい。QEでは、正方晶相の :math:`c/a`、斜方晶相の :math:`b` および :math:`c` も0.5%未満の誤差に収まった。一方、MLIPおよび一部の先行計算では、正方晶相の :math:`c/a` や斜方晶相の個別の格子定数で相対誤差が大きくなる傾向が見られた。これは、BaTiO₃の中間相ではTi/Oのオフセンター変位と格子歪みの結合が強く、わずかなポテンシャル面の違いが :math:`c/a` や :math:`b/c` の分裂に現れやすいためである。

なお、実験値は各相が有限温度で安定に存在する領域の代表値であるのに対し、計算値は0 Kでの最適化構造である。そのため、熱膨張や相転移温度近傍の揺らぎを含む実験値と完全に一致する必要はない。それでも、本結果ではDFTで0.5%前後、MLIPでも約1.5%程度の平均誤差に収まっており、BaTiO₃の格子定数を実験値と同じオーダーで再現できている。これは、適切な相拘束を用いれば、DFTおよびMLIPの双方がBaTiO₃多形の格子構造評価に有用であることを示している。

参考文献
--------

* :sup:`[1]` Kwei, G. H.; Lawson, A. C.; Billinge, S. J. L.; Cheong, S.-W.,
  "Structures of the ferroelectric phases of barium titanate,"
  *Journal of Physical Chemistry*, **97**, 2368, 1993.
  `https://doi.org/10.1021/j100112a043 <https://doi.org/10.1021/j100112a043>`_

* :sup:`[2]` Shirane, G.; Danner, H.; Pepinsky, R.,
  "Neutron diffraction study of orthorhombic BaTiO₃,"
  *Physical Review*, **105**, 856, 1957.
  `https://doi.org/10.1103/PhysRev.105.856 <https://doi.org/10.1103/PhysRev.105.856>`_

* :sup:`[3]` Amit Sehrawat et al., "Machine-learning interatomic potential for BaTiO3:
  phase transitions, domain walls, and grain boundaries,"
  *J. Phys.: Condens. Matter*, **38**, 015402, 2026.
  `https://doi.org/10.1088/1361-648X/ae2727 <https://doi.org/10.1088/1361-648X/ae2727>`_

* :sup:`[4]` Qi, Y.; Liu, S.; Grinberg, I.; Rappe, A. M.,
  "Atomistic description for temperature-driven phase transitions in BaTiO₃,"
  *Physical Review B*, **94**, 134308, 2016.
  `https://doi.org/10.1103/PhysRevB.94.134308 <https://doi.org/10.1103/PhysRevB.94.134308>`_
