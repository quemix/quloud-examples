.. _batio3-doc-stability:

==============================
安定基底状態
==============================

BaTiO₃ の 4 つの結晶相のうち、0 K で最もエネルギーが低いのはどの相でしょうか。
各相の最適化済みの格子を使い、原子座標を緩和して全エネルギーを比較します。
今回の DFT と機械学習原子間ポテンシャル（MLIP）の計算では、5 手法すべてで菱面体晶が最も低く、斜方晶、正方晶、立方晶の順に高くなりました。
菱面体晶と斜方晶の差は手法によっては 1 化学式単位あたり 1 meV 未満で、計算の収束条件に敏感です。

.. _batio3-stability:

.. figure:: ../Figure/BaTiO3/schematics-batio3-phase-transition-temperaturedependent.png
   :alt: BaTiO₃ の分極方向は、低温側から菱面体晶で〈111〉、斜方晶で〈110〉、正方晶で〈100〉。立方晶は非極性。
   :align: center
   :width: 92%

   BaTiO₃ の温度依存相系列と分極方向の概略図。Shu と Bhattacharya による整理に基づきます :sup:`[1]`。

正方晶、斜方晶、菱面体晶の結晶構造や原子変位は、X 線・中性子回折などで調べられてきました :sup:`[2,3]`。
第一原理計算に基づく有効ハミルトニアン研究では、局所的な極性ひずみと長距離相互作用の競合から、低温での安定性と相転移の順序が再現されています :sup:`[4,5]`。
以下では、菱面体晶、斜方晶、正方晶、立方晶をそれぞれ :math:`R`、:math:`O`、:math:`T`、:math:`C` と書きます。
4 相の空間群と分極の向きは、技術ノートの\ `4つの相と分極の向き <https://technical-notes.quemix.com/solid/ferroelectricity.html#batio3-four-phases>`__\ にまとめました。

.. _batio3-stability-inputs:

計算手順と代表的な入力ファイル
==============================

1. :doc:`lattice-constant` の手順に従い、各相の格子定数を最適化します。
2. 最適化した格子を固定し、原子座標を緩和します。
3. 最終構造の全エネルギーを 1 化学式単位あたりに換算します。手法ごとに菱面体晶の値を差し引き、相対エネルギーを求めます（技術ノートの\ `化学式単位あたりの相対エネルギー <https://technical-notes.quemix.com/electronic/pseudopotential_basis.html#energy-reference>`__）。

ここでは、構造最適化に用いた代表例として QE の入力ファイルのみを示します。
Quloud Job では、各相のジョブに含まれる ``QuloudJob.scf.in`` を以下の例で
置き換えることで、同じ形式の固定格子構造最適化を実行できます。入力中の
``calculation = 'relax'`` は格子を固定して原子位置のみを最適化する指定（`固定セル緩和 <https://technical-notes.quemix.com/electronic/structure_optimization.html#structure-optimization>`__）であり、
``ibrav``、``A``、``B``、``C``、``cosAB`` には、直前の格子最適化で得られた
各相の格子定数を用いています。原子位置の固定フラグは付けていないため、
Ti と O を含む内部座標は最適化されます。

.. list-table:: 固定格子構造最適化に用いた QE 入力の対応
   :header-rows: 1
   :widths: 18 10 34 38

   * - 相
     - ``ibrav``
     - 最適化済み格子
     - 役割
   * - 立方晶相
     - 1
     - :math:`a=b=c`
     - 非分極立方晶の基準構造
   * - 正方晶相
     - 6
     - :math:`a=b`, :math:`c`
     - :math:`\langle 100\rangle` 型分極をもつ相
   * - 斜方晶相
     - 8
     - :math:`a`, :math:`b`, :math:`c`
     - :math:`\langle 110\rangle` 型分極をもつ相
   * - 菱面体晶相
     - 5
     - :math:`a=b=c`, :math:`\alpha=\beta=\gamma`
     - :math:`\langle 111\rangle` 型分極をもつ相


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

QE
~~~~~~

.. raw:: html

   <details class="input-toggle">
     <summary>立方晶相</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">QuloudJob.scf.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('qe-cubic-input', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="qe-cubic-input" class="language-text">&amp;control
     calculation    = &#x27;relax&#x27;
     prefix         = &#x27;BaTiO3_cubic_QE_fixedcell_relax_from_latticeopt&#x27;
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
     A           = 4.0242627603
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
   ATOMIC_SPECIES
   Ba 137.327 Ba.pbe-spn-rrkjus_psl.1.0.0.UPF
   Ti  47.867 Ti.pbe-spn-rrkjus_psl.1.0.0.UPF
   O   15.999 O.pbe-nl-rrkjus_psl.1.0.0.UPF

   ATOMIC_POSITIONS {crystal}
   Ba  0.000000000000  0.000000000000  0.000000000000
   Ti  0.500000000000  0.500000000000  0.500000000000
   O   0.500000000000  0.500000000000  0.000000000000
   O   0.500000000000  0.000000000000  0.500000000000
   O   0.000000000000  0.500000000000  0.500000000000

   K_POINTS {automatic}
   6 6 6 0 0 0
   </code></pre>
     </div>
   </details>


.. raw:: html

   <details class="input-toggle">
     <summary>正方晶相</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">QuloudJob.scf.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('qe-tetragonal-input', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="qe-tetragonal-input" class="language-text">&amp;control
     calculation    = &#x27;relax&#x27;
     prefix         = &#x27;BaTiO3_tetragonal_QE_fixedcell_relax_from_latticeopt&#x27;
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
     A           = 4.0151174639
     C           = 4.0680532926
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
   ATOMIC_SPECIES
   Ba 137.327 Ba.pbe-spn-rrkjus_psl.1.0.0.UPF
   Ti  47.867 Ti.pbe-spn-rrkjus_psl.1.0.0.UPF
   O   15.999 O.pbe-nl-rrkjus_psl.1.0.0.UPF

   ATOMIC_POSITIONS {crystal}
   Ba  0.000000000000  0.000000000000  0.000000000000
   Ti  0.499983187300  0.499983187300  0.519965796700
   O   0.499983187300  0.499983187300  0.984935211100
   O   0.499983187300  0.000000000000  0.484968098900
   O   0.000000000000  0.499983187300  0.484968098900

   K_POINTS {automatic}
   6 6 6 0 0 0
   </code></pre>
     </div>
   </details>


.. raw:: html

   <details class="input-toggle">
     <summary>斜方晶相</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">QuloudJob.scf.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('qe-orthorhombic-input', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="qe-orthorhombic-input" class="language-text">&amp;control
     calculation    = &#x27;relax&#x27;
     prefix         = &#x27;BaTiO3_orthorhombic_polar110_QE_fixedcell_relax_from_latticeopt&#x27;
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
     A           = 4.0246783931
     B           = 5.6925106359
     C           = 5.6914525484
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
   ATOMIC_SPECIES
   Ba 137.327 Ba.pbe-spn-rrkjus_psl.1.0.0.UPF
   Ti  47.867 Ti.pbe-spn-rrkjus_psl.1.0.0.UPF
   O   15.999 O.pbe-nl-rrkjus_psl.1.0.0.UPF

   ATOMIC_POSITIONS {crystal}
   Ba  0.000000000000  0.000000000000  0.000000000000
   Ba  0.000000000000  0.500008826700  0.500006672400
   Ti  0.502938513500  0.003000053000  0.500006672400
   Ti  0.502938513500  0.503008879700  0.000000000000
   O   0.498439063500  0.248504386900  0.250003336200
   O   0.498439063500  0.748513213600  0.750010008600
   O   0.498439063500  0.248504386900  0.750010008600
   O   0.498439063500  0.748513213600  0.250003336200
   O   0.998377943700  0.998517626900  0.500006672400
   O   0.998377943700  0.498508800200  0.000000000000

   K_POINTS {automatic}
   6 4 4 0 0 0
   </code></pre>
     </div>
   </details>


.. raw:: html

   <details class="input-toggle">
     <summary>菱面体晶相</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">QuloudJob.scf.in</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('qe-rhombohedral-input', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="qe-rhombohedral-input" class="language-text">&amp;control
     calculation    = &#x27;relax&#x27;
     prefix         = &#x27;BaTiO3_rhombohedral_QE_fixedcell_relax_from_latticeopt&#x27;
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
     A           = 4.0265564845
     cosAB       = 0.004402895456
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
   ATOMIC_SPECIES
   Ba 137.327 Ba.pbe-spn-rrkjus_psl.1.0.0.UPF
   Ti  47.867 Ti.pbe-spn-rrkjus_psl.1.0.0.UPF
   O   15.999 O.pbe-nl-rrkjus_psl.1.0.0.UPF

   ATOMIC_POSITIONS {crystal}
   Ba  0.000000000000  0.000000000000  0.000000000000
   Ti  0.515099343400  0.515099343400  0.515099343400
   O   0.485093556400  0.485093556400  0.000000000000
   O   0.485093556400  0.000000000000  0.485093556400
   O   0.000000000000  0.485093556400  0.485093556400

   K_POINTS {automatic}
   6 6 6 0 0 0
   </code></pre>
     </div>
   </details>


MLIP
~~~~

MLIP には、CHGNet、SevenNet（モデル ``7net-mf-ompa``）、FairChem（モデル ``uma-s-1p1``）を用いました。

以下は Quloud の ASE および LAMMPS ジョブで使う入力ファイル例です。ASE では ``ase.in``、LAMMPS では ``in.QuloudJob`` を置き換えて使います。構造データは各相のジョブに含まれるものを利用するため、同じ入力形式を各相に適用できます。

.. list-table:: MLIP入力の対応
   :header-rows: 1
   :widths: 24 26 50

   * - 手法
     - ファイル名
     - 主な設定
   * - ASE SevenNet
     - ``ase.in``
     - ``provider: "7net"``, ``latopt: false``
   * - ASE FairChem
     - ``ase.in``
     - ``provider: "fairchem"``, ``latopt: false``
   * - LAMMPS CHGNet
     - ``in.QuloudJob``
     - CHGNet 用 LAMMPS 入力例

.. raw:: html

   <details class="input-toggle">
     <summary>ASE SevenNet</summary>
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
       &quot;latopt&quot;: false
     },
     &quot;provider&quot;: &quot;7net&quot;,
     &quot;model_name&quot;: &quot;7net-mf-ompa&quot;
   }</code></pre>
     </div>
   </details>
   <details class="input-toggle">
     <summary>ASE FairChem</summary>
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
     <summary>LAMMPS CHGNet</summary>
     <div class="input-toggle-body">
       <div class="input-copy-row">
         <span class="input-file-name">in.QuloudJob</span>
         <button type="button" class="copy-input-button" onclick="copyInputBlock('input-mlip-chgnet-lammps', this)">Copy</button>
       </div>
       <pre class="input-code"><code id="input-mlip-chgnet-lammps" class="language-text">
         # Generated from CHGNet/LAMMPS lattice-optimized BaTiO3 structure
         # Fixed-cell structural optimization: atomic positions are relaxed, lattice is held fixed.
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
         minimize 1.0e-15 1.0e-7 1000 10000
         write_data QuloudJob.out.lmp
       </code></pre>
     </div>
   </details>


.. _batio3-stability-results:

結果の概要
==========

本計算では、BaTiO₃ の代表的な四つの多形を対象とし、0 K における相対安定性を
DFT および MLIP により比較しました。ここで示す全エネルギーは、前段階で最適化した
格子定数を固定し、その格子上で原子位置を最適化して得たものです。したがって、
この比較は、格子歪みの特徴を各相に保ったうえで、内部座標の緩和により得られる
0 K の静的エネルギー順位を評価するものです。

.. figure:: ../Figure/BaTiO3/batio3_relative_phase_energies_updated-rev.png
   :alt: BaTiO3 relative phase energies
   :align: center
   :width: 92%

   菱面体晶相を基準にした BaTiO₃ 各相の相対エネルギー。

エネルギーは各手法で得られた菱面体晶相を基準とし、1 化学式単位あたりの相対エネルギー
:math:`\Delta E = E_{\mathrm{phase}} - E_R` として整理しました。5 手法は基底関数、擬ポテンシャル、
エネルギー基準、または学習されたエネルギー面が異なるので、比べられるのは同じ手法の中での
相対エネルギー差と安定性の順序です。

.. list-table:: BaTiO₃ 各相の相対エネルギー（meV/化学式単位）
   :header-rows: 1
   :widths: 22 16 16 18 20 20
   :class: wrap-table

   * - 相
     - OpenMX-DFT
     - QE-DFT
     - SevenNet-ASE
     - FairChem-ASE
     - CHGNet-LAMMPS
   * - 斜方晶相 :math:`O`
     - 0.136
     - 2.469
     - 4.260
     - 3.967
     - 0.763
   * - 正方晶相 :math:`T`
     - 1.361
     - 10.041
     - 6.580
     - 8.587
     - 5.043
   * - 立方晶相 :math:`C`
     - 18.232
     - 45.608
     - 41.195
     - 45.510
     - 64.320

すべての手法で、菱面体晶相が最も低いエネルギーを示し、次に斜方晶相、正方晶相、
立方晶相の順にエネルギーが高くなりました。したがって、本計算で得られた 0 K の
安定性順序は

.. math::

   \mathrm{Rhombohedral} < \mathrm{Orthorhombic} <
   \mathrm{Tetragonal} < \mathrm{Cubic}

であり、実験的に知られている低温側から高温側への相系列、および第一原理有効
ハミルトニアンに基づく先駆的研究の結果と整合しています :sup:`[2,4,5]`。

.. _batio3-stability-methods:

DFT と MLIP の比較
===================

DFT 計算では、OpenMX-DFT と QE-DFT のいずれも
:math:`R < O < T < C` の順序を与えました。OpenMX-DFT では
:math:`O-R = 0.136~\mathrm{meV/f.u.}` と非常に小さく、菱面体晶相と斜方晶相は
ほぼ縮退しています。一方、QE-DFT では :math:`O-R = 2.469~\mathrm{meV/f.u.}`、
:math:`T-R = 10.041~\mathrm{meV/f.u.}`、:math:`C-R = 45.608~\mathrm{meV/f.u.}`
であり、相の対称性が高くなるにつれて相対エネルギーが段階的に上昇します。
これは、0 K の静的エネルギー曲面において、強誘電歪みをもつ低対称相が、
非分極の立方晶相より安定化されることを示しています。

MLIP 計算でも同じ順序が得られました。SevenNet-ASE と FairChem-ASE では、
斜方晶相は菱面体晶相より約 :math:`4~\mathrm{meV/f.u.}` 高く、正方晶相は
さらに高いです。CHGNet-LAMMPS では :math:`O-R = 0.763~\mathrm{meV/f.u.}` と
小さい一方、立方晶相は :math:`64.320~\mathrm{meV/f.u.}` 高く評価されました。
MLIP の種類によってエネルギー差の大きさは異なりますが、基底状態の相安定性順序は
DFT と一致しています。このことは、MLIP を用いた構造最適化でも、BaTiO₃ の代表的な
多形間の相対安定性を定性的に再現できることを示しています。

ただし、:math:`R` と :math:`O` のエネルギー差は、OpenMX-DFT と
CHGNet-LAMMPS では 1 :math:`\mathrm{meV/f.u.}` 以下であり、数値収束、格子拘束、
原子位置最適化の条件に対して敏感です。このため、これら二つの相の順位を
議論する場合には、k 点密度、カットオフ、最終構造の分極方向、力の収束条件を
明記する必要があります。一方で、全手法に共通して立方晶相が最も高いエネルギーを
示す点は明確であり、非分極立方晶相が 0 K の基底状態ではないことをよく表しています。

物理的な解釈
============

BaTiO₃ の相安定性は、Ti 原子のオフセンター変位と O 八面体の応答による
`極性ソフトモード <https://technical-notes.quemix.com/solid/soft_mode.html#polar-soft-mode>`__\ と、格子歪みとの結合に強く支配されます。
各相の分極の向き（:math:`T` は :math:`\langle 100\rangle`、:math:`O` は :math:`\langle 110\rangle`、
:math:`R` は :math:`\langle 111\rangle`）は、:math:`a`、:math:`b`、:math:`c` と格子角の歪みと結びついています。
この関係は、分域（ドメイン）構造や巨視的応答を議論する上でも重要です :sup:`[1]`\ （技術ノートの\ `分域と分域壁 <https://technical-notes.quemix.com/solid/ferroelectricity.html#ferroelectric-domains>`__）。

Senn らの局所構造解析によれば、Ti の局所的なオフセンター変位はどの相でも菱面体的で、
相の違いは変位の相関の向きと格子歪みの組み合わせに現れます :sup:`[6]`\ （技術ノートの\ `局所的なTiの変位と平均構造 <https://technical-notes.quemix.com/solid/ferroelectricity.html#fe-local-average>`__）。
したがって、本計算で各相の分極方向と格子の特徴を保ちながら最適化した
ことは、相安定性を比較する上で重要です。

また、Nishimatsu らは、BaTiO₃ の相転移温度や分極歪みが、DFT の
`交換相関汎関数 <https://technical-notes.quemix.com/electronic/exchange_correlation.html#exchange-correlation-functional>`__\ と
格子定数に強く依存することを示しています :sup:`[7]`。本結果でも、手法によって
相対エネルギーの大きさは異なります。しかし、DFT と MLIP の両方で同じ
:math:`R < O < T < C` の順序が得られたことは、今回の構造最適化手順が
BaTiO₃ の 0 K 相安定性を捉える上で妥当であることを支持しています。

結論と今後の展望
================

本計算では、OpenMX-DFT、QE-DFT、SevenNet-ASE、FairChem-ASE、CHGNet-LAMMPS の
すべてにおいて、BaTiO₃ の 0 K 安定性順序として

.. math::

   R < O < T < C

が得られました。この結果は、低温で菱面体晶相が最安定となり、温度上昇に伴って
斜方晶相、正方晶相、立方晶相へ移るという実験的な相転移系列と整合します。
また、DFT だけでなく MLIP でも同じ相安定性順序を再現できることから、
MLIP は BaTiO₃ の構造探索や有限温度シミュレーションの初期評価に有用であると
考えられます。

一方で、0 K の静的エネルギー順位だけでは、相転移温度や有限温度での安定性は決まりません。
残る課題は、(i) フォノンによる動的安定性の確認、(ii) 分子動力学またはモンテカルロ法による
有限温度効果の評価、(iii) 自由エネルギー、エントロピー、熱膨張を含む相境界の解析です
（技術ノートの\ `虚数振動数と動的安定性 <https://technical-notes.quemix.com/solid/phonon.html#imaginary-frequency>`__、
`零点振動と零点エネルギー <https://technical-notes.quemix.com/solid/phonon_thermal.html#zero-point-vibration>`__）。
とくに菱面体晶相と斜方晶相のエネルギー差が小さいため、有限温度効果、零点振動、
格子歪みと分極の結合が相転移挙動に大きく寄与する可能性があります。
この結果は、フォノン安定性、ドメイン構造、粒界構造などを調べるための 0 K の基準になります。
温度を上げたときに現れる相は、:doc:`構造相転移 <phase_transition>` の昇温計算で調べます。

参考文献
========

* :sup:`[1]` Shu, Y. C.; Bhattacharya, K.,
  "Domain patterns and macroscopic behaviour of ferroelectric materials,"
  *Philosophical Magazine B*, **81**, 2021--2054, 2001.
  `https://doi.org/10.1080/13642810108208556 <https://doi.org/10.1080/13642810108208556>`_

* :sup:`[2]` Kwei, G. H.; Lawson, A. C.; Billinge, S. J. L.; Cheong, S.-W.,
  "Structures of the ferroelectric phases of barium titanate,"
  *Journal of Physical Chemistry*, **97**, 2368, 1993.
  `https://doi.org/10.1021/j100112a043 <https://doi.org/10.1021/j100112a043>`_

* :sup:`[3]` Shirane, G.; Danner, H.; Pepinsky, R.,
  "Neutron diffraction study of orthorhombic BaTiO₃,"
  *Physical Review*, **105**, 856, 1957.
  `https://doi.org/10.1103/PhysRev.105.856 <https://doi.org/10.1103/PhysRev.105.856>`_

* :sup:`[4]` Zhong, W.; Vanderbilt, D.; Rabe, K. M.,
  "Phase transitions in BaTiO₃ from first principles,"
  *Physical Review Letters*, **73**, 1861--1864, 1994.
  `https://doi.org/10.1103/PhysRevLett.73.1861 <https://doi.org/10.1103/PhysRevLett.73.1861>`_

* :sup:`[5]` Zhong, W.; Vanderbilt, D.; Rabe, K. M.,
  "First-principles theory of ferroelectric phase transitions for perovskites:
  The case of BaTiO₃,"
  *Physical Review B*, **52**, 6301--6312, 1995.
  `https://doi.org/10.1103/PhysRevB.52.6301 <https://doi.org/10.1103/PhysRevB.52.6301>`_

* :sup:`[6]` Senn, M. S.; Keen, D. A.; Lucas, T. C. A.; Hriljac, J. A.;
  Goodwin, A. L., "Emergence of long-range order in BaTiO₃ from local
  symmetry-breaking distortions," *Physical Review Letters*, **116**, 207602, 2016.
  `https://doi.org/10.1103/PhysRevLett.116.207602 <https://doi.org/10.1103/PhysRevLett.116.207602>`_

* :sup:`[7]` Nishimatsu, T.; Iwamoto, M.; Kawazoe, Y.; Waghmare, U. V.,
  "First-principles accurate total-energy surfaces for polar structural distortions
  of BaTiO₃, PbTiO₃, and SrTiO₃: Consequences to structural transition temperatures,"
  *Physical Review B*, **82**, 134106, 2010.
  `https://doi.org/10.1103/PhysRevB.82.134106 <https://doi.org/10.1103/PhysRevB.82.134106>`_
