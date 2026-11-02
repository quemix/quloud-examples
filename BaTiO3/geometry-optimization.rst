========================================
BaTiO₃構造最適化の計算例
========================================

目的と背景
----------------------------------------------------------------------

本例では、正方晶強誘電 BaTiO₃ に対して、格子定数および格子角を固定した構造最適化を行い、
OpenMX による密度汎関数理論計算と、CHGNet、SevenNet、FairChem による機械学習原子間ポテンシャル計算を比較する。
ここで扱う最適化は、格子そのものを変化させる格子最適化ではなく、固定された正方晶格子内における原子内部座標の緩和である。

BaTiO₃ は代表的なペロブスカイト型強誘電体であり、理想立方晶構造からのわずかな正方晶歪みと、
Ti 原子および O 原子の相対変位によって強誘電性を示す。
実験的には、BaTiO₃ が正方晶構造をとることが古くから報告されている。
また、中性子散乱実験では、強誘電相転移とソフトモードの関係が明らかにされている。
第一原理計算では、Ti 3d 軌道と O 2p 軌道の混成が、BaTiO₃ の強誘電安定化に重要であると理解されている。

本計算例の目的は、各計算手法が正方晶 BaTiO₃ の強誘電変位をどの程度保持し、
どの原子が主に緩和するかを比較することである。
特に、Ti-O 相対変位、酸素八面体の歪み、固定格子条件における構造安定性に注目する。

入力ファイル例
----------------------------------------------------------------------

以下の入力ファイルは、結果表や考察の前に確認できるようにまとめている。
安定基底状態の計算例と同じく、各入力は展開式のブロックとして表示し、必要に応じてコピーして利用できる。

.. raw:: html

   <style>
   .input-toggle { border: 1px solid #d0d7de; border-radius: 10px; margin: 0.85em 0; background: #f6f8fa; box-shadow: 0 1px 2px rgba(27, 31, 36, 0.04); }
   .input-toggle summary { cursor: pointer; padding: 0.78em 1.0em; font-weight: 700; color: #24292f; background: linear-gradient(180deg, #f6f8fa 0%, #eef1f4 100%); border-radius: 10px; list-style-position: outside; }
   .input-toggle summary:hover { background: #eef1f4; }
   .input-toggle[open] summary { border-bottom: 1px solid #d0d7de; border-radius: 10px 10px 0 0; }
   .input-toggle-body { padding: 0; background: #ffffff; border-radius: 0 0 10px 10px; }
   .input-copy-row { display: flex; align-items: center; justify-content: space-between; gap: 0.75em; padding: 0.55em 0.75em; background: #f6f8fa; border-bottom: 1px solid #d0d7de; }
   .input-file-name { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; font-size: 0.86em; color: #57606a; }
   .copy-input-button { display: inline-flex; align-items: center; justify-content: center; gap: 0.32em; min-width: 4.9em; border: 1px solid #d0d7de; background: #f6f8fa; color: #24292f; border-radius: 6px; padding: 0.28em 0.62em; font-size: 0.80em; line-height: 1.25; font-weight: 600; cursor: pointer; }
   .copy-input-button::before { content: "Copy"; font-size: 0.80em; color: #57606a; }
   .copy-input-button.copied { color: #1a7f37; border-color: #a6d9b6; background: #dafbe1; }
   .copy-input-button.copied::before { content: "OK"; color: #1a7f37; }
   .input-code { display: block; margin: 0; max-height: 42rem; overflow-y: auto; overflow-x: auto; white-space: pre-wrap; overflow-wrap: anywhere; background: #f6f8fa; border: 0; border-radius: 0 0 10px 10px; padding: 1.0em; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; font-size: 0.84em; line-height: 1.45; color: #24292f; text-align: left; direction: ltr; tab-size: 2; }
   .input-code code { display: block; white-space: pre-wrap; overflow-wrap: anywhere; }
   </style>
   <script>
   window.copyInputBlock = window.copyInputBlock || function(id, button) {
       var el = document.getElementById(id);
       if (!el) return;
       var text = el.innerText || el.textContent || '';
       function showCopied() { var old = button.textContent; button.textContent = 'Copied'; button.classList.add('copied'); window.setTimeout(function() { button.textContent = old; button.classList.remove('copied'); }, 1400); }
       function fallbackCopy() { var ta = document.createElement('textarea'); ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.left = '-9999px'; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); showCopied(); } catch (err) { console.error(err); } document.body.removeChild(ta); }
       if (navigator.clipboard && window.isSecureContext) { navigator.clipboard.writeText(text).then(showCopied).catch(fallbackCopy); } else { fallbackCopy(); }
   };
   </script>

QE：固定格子・原子座標緩和
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

以下は、安定基底状態の計算例で用いた正方晶相の QE 入力例を、構造最適化の計算例でもそのまま利用する場合の設定である。
Quloud Job では、各ジョブに含まれる ``QuloudJob.scf.in`` を以下の例で置き換え、
``calculation = 'relax'`` によって格子を固定したまま原子位置のみを最適化する。

.. raw:: html

   <details class="input-toggle">
     <summary>QE fixed-cell atomic relaxation</summary>
     <div class="input-toggle-body">

.. code-block:: text

   &control
     calculation    = 'relax'
     prefix         = 'BaTiO3_tetragonal_QE_fixedcell_relax_from_latticeopt'
     pseudo_dir     = './'
     outdir         = './work'
     verbosity      = 'high'
     tstress        = .true.
     tprnfor        = .true.
     etot_conv_thr  = 1.0d-5
     forc_conv_thr  = 1.0d-4
     nstep          = 100
   /
   &system
     ibrav       = 6
     A           = 4.0151174639
     C           = 4.0680532926
     nat         = 5
     ntyp        = 3
     ecutwfc     = 52.0
     ecutrho     = 575.0
     input_dft   = 'PBE'
     tot_charge  = 0.0
     occupations = 'fixed'
     nspin       = 1
   /
   &electrons
     conv_thr         = 1.0d-10
     mixing_beta      = 0.7
     electron_maxstep = 100
   /
   &ions
     ion_dynamics = 'bfgs'
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

.. raw:: html

     </div>
   </details>


OpenMX：固定格子・原子座標緩和
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

以下は、OpenMX による正方晶 BaTiO₃ の固定格子構造最適化入力例である。
格子ベクトルは固定し、原子座標のみを緩和する。

.. raw:: html

   <details class="input-toggle">
     <summary>OpenMX fixed-cell atomic relaxation</summary>
     <div class="input-toggle-body">

.. code-block:: text

   System.CurrrentDirectory  ./
   System.Name               BTO_Tet_Opt
   DATA.PATH                 /usr/local/rsdft/DFT_DATA19

   Species.Number 3
   <Definition.of.Atomic.Species
   Ba  Ba10.0-s3p2d2f1  Ba_PBE19
   Ti  Ti7.0-s3p2d2f1   Ti_PBE19
   O   O6.0-s3p2d2      O_PBE19
   Definition.of.Atomic.Species>

   Atoms.Number 5
   Atoms.SpeciesAndCoordinates.Unit FRAC
   <Atoms.SpeciesAndCoordinates
   1 Ba  0.0000000000  0.0000000000  0.0000000000  5.0  5.0
   2 Ti  0.4999831873  0.4999831873  0.5199657967  6.0  6.0
   3 O   0.4999831873  0.4999831873  0.9849352111  3.0  3.0
   4 O   0.4999831873  0.0000000000  0.4849680989  3.0  3.0
   5 O   0.0000000000  0.4999831873  0.4849680989  3.0  3.0
   Atoms.SpeciesAndCoordinates>

   Atoms.UnitVectors.Unit Ang
   <Atoms.UnitVectors
   4.0151174639  0.0000000000  0.0000000000
   0.0000000000  4.0151174639  0.0000000000
   0.0000000000  0.0000000000  4.0680532926
   Atoms.UnitVectors>

   scf.XcType                 GGA-PBE
   scf.SpinPolarization       off
   scf.ElectronicTemperature  300.0
   scf.energycutoff           500
   scf.maxIter                500
   scf.EigenvalueSolver       band
   scf.Kgrid                  8 8 8
   scf.criterion              1.0e-8

   MD.Type                    BFGS
   MD.maxIter                 500
   MD.Opt.criterion           1.0e-4
   MD.Opt.Init.Hessian        Schlegel

.. raw:: html

     </div>
   </details>


CHGNet：固定格子・z方向のみの原子座標緩和
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

以下は、CHGNet の入力例である。
正方晶の面内原子配置を保持するため、x 方向および y 方向の力をゼロにし、z 方向のみを緩和する。

.. raw:: html

   <details class="input-toggle">
     <summary>CHGNet z-only fixed-cell relaxation</summary>
     <div class="input-toggle-body">

.. code-block:: text

   # 固定格子・正方晶強誘電 BaTiO3 の CHGNet 構造最適化
   # 格子定数と格子角は固定する
   # 正方晶 P4mm 的な面内原子配置を保持する
   # c 軸方向の強誘電変位のみを緩和する

   units metal
   boundary p p p
   atom_style atomic

   read_data QuloudJob.lmp

   pair_style chgnet ../../../../../../../../CHGNET
   pair_coeff * * 0.3.0 Ba Ti O

   neighbor 2.0 bin
   neigh_modify every 1 delay 0 check yes

   thermo_style custom step pe etotal temp vol press pxx pyy pzz fmax
   thermo 10

   dump 1 all custom 5 QuloudJob.lammpstrj id type x y z fx fy fz
   dump_modify 1 sort id

   # x 方向および y 方向の力をゼロにし、z 方向のみを緩和する
   fix keep_tet all setforce 0.0 0.0 NULL

   min_style fire
   minimize 1.0e-15 1.0e-7 1000 10000

   unfix keep_tet

   write_data QuloudJob.out.lmp
   write_dump all custom QuloudJob.final.lammpstrj id type x y z fx fy fz

.. raw:: html

     </div>
   </details>


SevenNet：固定格子・原子座標緩和
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

以下は、SevenNet による固定格子構造最適化入力例である。
``latopt`` を ``false`` にすることで、格子最適化を行わず、原子座標のみを緩和する。

.. raw:: html

   <details class="input-toggle">
     <summary>SevenNet fixed-cell atomic relaxation</summary>
     <div class="input-toggle-body">

.. code-block:: json

   {
     "mode": "opt",
     "opt": {
       "fmax": 0.01,
       "ntime": 100,
       "latopt": false
     },
     "provider": "7net",
     "model_name": "7net-mf-ompa"
   }

.. raw:: html

     </div>
   </details>


FairChem：固定格子・原子座標緩和
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

以下は、FairChem による固定格子構造最適化入力例である。
SevenNet と同様に、格子は固定し、原子座標のみを緩和する。

.. raw:: html

   <details class="input-toggle">
     <summary>FairChem fixed-cell atomic relaxation</summary>
     <div class="input-toggle-body">

.. code-block:: json

   {
     "mode": "opt",
     "opt": {
       "fmax": 0.01,
       "ntime": 100,
       "latopt": false
     },
     "provider": "fairchem",
     "model_name": "uma-s-1p1"
   }


.. raw:: html

     </div>
   </details>


OpenMXによる構造最適化
----------------------------------------------------------------------

計算条件
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

OpenMX 計算では、正方晶格子を固定し、原子座標のみを緩和した。
交換相関汎関数には GGA-PBE を用い、k 点格子は 8 x 8 x 8、エネルギーカットオフは 500 Ry とした。
格子条件は、安定基底状態の計算例と同じ正方晶の参考格子設定を用いた。
初期構造は、すでに正方晶強誘電変位を含む BaTiO₃ 構造である。

.. list-table:: 固定格子の参考設定
   :header-rows: 1
   :widths: 25 25 25 25

   * - 手法
     - a (Å)
     - c (Å)
     - c/a
   * - OpenMX / QE 参考設定
     - 4.0151174639
     - 4.0680532926
     - 1.01318

最適化手法の比較
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

OpenMX では、DIIS、EF、BFGS、RF、Opt の複数の最適化手法を比較した。
すべての手法でほぼ同一の最終エネルギーと最終構造が得られた。
したがって、本構造最適化は、最適化アルゴリズムに強く依存しない安定な結果であると判断できる。

.. list-table:: OpenMX による固定格子構造最適化結果
   :header-rows: 1
   :widths: 18 18 24 24 20

   * - 最適化手法
     - イオンステップ数
     - 最終エネルギー (Ha)
     - エネルギー低下 (meV/cell)
     - 最終最大力 (eV/Å)
   * - DIIS
     - 10
     - -135.5003359
     - 9.37
     - 0.00357
   * - EF
     - 9
     - -135.5003355
     - 9.36
     - 0.00216
   * - BFGS
     - 9
     - -135.5003356
     - 9.36
     - 0.00364
   * - RF
     - 10
     - -135.5003357
     - 9.36
     - 0.00259
   * - Opt
     - 10
     - -135.5003355
     - 9.36
     - 0.00394

OpenMX では、構造最適化によるエネルギー低下は約 9.36 meV/5原子セルであった。
この値は比較的小さいため、初期構造はすでに正方晶強誘電相の局所安定構造に近かったと考えられる。

原子変位の評価
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

初期構造から最終構造への主な変化は、Ti ではなく酸素副格子に現れた。
Ti 原子の z 方向位置はほとんど変化せず、apical O は負方向へ、equatorial O は正方向へ緩和した。

.. list-table:: OpenMX における初期構造から最終構造への z 方向変位
   :header-rows: 1
   :widths: 30 30 40

   * - 原子
     - 変位量 Δz (Å)
     - 物理的解釈
   * - Ba
     - +0.00268
     - ほぼ固定された基準原子として振る舞う
   * - Ti
     - +0.00004
     - Ti の強誘電オフセンタリングはほぼ保持される
   * - O apical
     - -0.02956
     - c 軸方向の Ti-O 非対称性を強める
   * - O equatorial
     - +0.01322
     - 酸素面内位置が穏やかに緩和する

Ba を基準にした最終強誘電変位は以下の通りである。

.. list-table:: OpenMX における Ba 基準の最終強誘電変位
   :header-rows: 1
   :widths: 30 30 40

   * - 原子
     - 最終変位 (Å)
     - 解釈
   * - Ti
     - +0.078
     - Ti が正方向へオフセンター変位している
   * - O apical
     - -0.093
     - Ti-O 軸方向結合の非対称性を形成する
   * - O equatorial
     - -0.051
     - 酸素八面体の極性歪みに寄与する

この結果は、BaTiO₃ の強誘電性が Ti-O 相対変位に由来するという既知の物理描像と整合的である。
特に、Ti 原子が強誘電方向へ変位し、酸素八面体が非対称に歪むという特徴は、
実験構造および第一原理研究で示されてきた BaTiO₃ の強誘電構造とよく対応している。

機械学習ポテンシャルによる構造最適化
----------------------------------------------------------------------

計算条件
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

機械学習原子間ポテンシャル計算では、CHGNet、SevenNet、FairChem を用いた。
OpenMX と同様に、格子定数と格子角は固定し、原子位置のみを緩和した。
ただし、機械学習ポテンシャル計算で用いた固定格子は OpenMX の固定格子とわずかに異なる。

.. list-table:: OpenMX と機械学習ポテンシャルの固定格子比較
   :header-rows: 1
   :widths: 25 25 25 25

   * - 計算手法
     - a (Å)
     - c (Å)
     - c/a
   * - OpenMX
     - 4.0151174639
     - 4.0680532926
     - 1.01318
   * - 機械学習ポテンシャル
     - 4.01512
     - 4.06805
     - 1.01318

この差は小さいため、内部変位の傾向比較には有効である。
一方で、格子が完全には一致していないため、厳密な同一格子比較ではない。
また、密度汎関数理論計算と機械学習ポテンシャル計算ではエネルギーの基準が異なるため、
絶対エネルギーを直接比較してはならない。
比較すべき量は、力の収束、強誘電変位、Ti-O 結合距離、および正方晶対称性の保持である。

計算結果の概要
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: 機械学習ポテンシャルによる固定格子構造最適化結果
   :header-rows: 1
   :widths: 20 22 22 30 26

   * - 手法
     - エネルギー低下 (meV/cell)
     - 最終最大力 (eV/Å)
     - 構造の特徴
     - 判定
   * - CHGNet
     - 16.31
     - 0.00707
     - 面内座標を保持し、z方向のみ緩和
     - 対称性保持には有効だが、酸素変位は過大
   * - SevenNet
     - 14.13
     - 0.00776
     - 正方晶的構造を保持
     - 良好
   * - FairChem
     - 14.61
     - 0.00648
     - 正方晶的構造を保持
     - 本構造・本評価量では OpenMX に最も近い

CHGNet では、LAMMPS 入力中で ``fix keep_tet all setforce 0.0 0.0 NULL`` を用いた。
これにより、x 方向および y 方向の力をゼロにし、z 方向の力のみを有効にした。
その結果、格子定数、格子角、面内原子配置を保ったまま、c 軸方向の強誘電変位だけを緩和できた。

CHGNet の最小化は 50 ステップで停止し、エネルギーは -42.036781 eV から -42.053089 eV へ低下した。
エネルギー低下は 16.31 meV/5原子セルであり、最終最大力成分は 0.00707 eV/Å であった。
固定格子計算であるため、残留圧力は格子最適化の未実施を反映しており、
原子座標緩和の収束判定には主として力を用いる。

CHGNet における原子変位
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

CHGNet では、面内座標は保持されたが、z 方向の内部変位は OpenMX と異なる傾向を示した。
特に、Ba 原子の z 方向移動が比較的大きく、Ba を基準にした相対変位で見ると、
Ti 変位は小さくなり、酸素変位は OpenMX より大きくなった。

.. list-table:: CHGNet における初期構造から最終構造への z 方向変位
   :header-rows: 1
   :widths: 30 30 40

   * - 原子
     - 変位量 Δz (Å)
     - 解釈
   * - Ba
     - +0.04061
     - z 方向に比較的大きく移動する
   * - Ti
     - +0.00174
     - Ti 自身の絶対位置変化は小さい
   * - O apical
     - -0.04686
     - c 軸方向の酸素変位が大きい
   * - O equatorial
     - -0.00226
     - 絶対座標では小さく負方向へ移動する

Ba を基準にした最終強誘電変位は以下である。

.. list-table:: OpenMX と機械学習ポテンシャルにおける Ba 基準の最終強誘電変位
   :header-rows: 1
   :widths: 25 25 25 25

   * - 手法
     - Ti (Å)
     - O apical (Å)
     - O equatorial (Å)
   * - OpenMX
     - +0.078
     - -0.093
     - -0.051
   * - CHGNet
     - +0.042
     - -0.149
     - -0.104
   * - SevenNet
     - +0.066
     - -0.123
     - -0.075
   * - FairChem
     - +0.068
     - -0.121
     - -0.071

この結果から、CHGNet は正方晶的な面内座標を保持するが、
Ba 基準で見た Ti の強誘電変位は OpenMX より小さく、酸素変位は OpenMX よりかなり大きい。
したがって、CHGNet は「正方晶性を保つ」という観点では有効である一方、
この拘束条件と初期構造における OpenMX の内部変位との一致度は、FairChem および SevenNet より低い。
これはモデル全般の優劣ではなく、本構造に対する局所的な比較である。

Ti-O 局所構造の比較
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ti-O 結合距離を見ると、CHGNet では面内拘束により正方晶的な面内配置が保持された。
一方、apical Ti-O 結合の短長差は OpenMX より大きく、酸素八面体の極性歪みを過大評価する傾向が残る。

.. list-table:: Ti-O 局所構造の比較
   :header-rows: 1
   :widths: 25 25 25 25 25

   * - 手法
     - 短い apical Ti-O (Å)
     - 長い apical Ti-O (Å)
     - apical 結合差 (Å)
     - equatorial Ti-O (Å)
   * - OpenMX
     - 1.860
     - 2.203
     - 0.343
     - 2.010
   * - CHGNet
     - 1.843
     - 2.225
     - 0.382
     - 2.013
   * - SevenNet
     - 1.846
     - 2.222
     - 0.376
     - 2.012
   * - FairChem
     - 1.845
     - 2.223
     - 0.378
     - 2.012

CHGNet、SevenNet、FairChem は、equatorial Ti-O 距離については OpenMX に近い値を与える。
しかし、apical Ti-O の結合差は OpenMX より大きく、
機械学習ポテンシャルが酸素八面体の極性歪みを強めに予測していることが分かる。

考察と比較
----------------------------------------------------------------------

密度汎関数理論計算と機械学習ポテンシャル計算の役割
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

密度汎関数理論計算は電子状態を明示的に解くため、Ti-O 軌道混成、結合性、強誘電安定性を物理的に評価できる。
そのため、BaTiO₃ のように微小な原子変位と電子構造が強く結び付いた強誘電体では、
密度汎関数理論計算は基準計算として重要である。

一方、機械学習原子間ポテンシャル計算は学習済みポテンシャルを用いるため、
密度汎関数理論計算より高速に構造緩和を行える。
そのため、多数の構造を調べるスクリーニングや、分子動力学計算には有用である。
ただし、学習データやモデルの表現能力に依存するため、
特定の構造歪みを過大または過小に評価する可能性がある。

OpenMX と既往研究の対応
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

OpenMX の結果では、Ti の強誘電オフセンタリングが保持され、酸素副格子が主に緩和した。
これは、BaTiO₃ の強誘電性が Ti-O 相対変位および酸素八面体の歪みによって特徴づけられるという
既往研究の理解と整合する。

実験的な正方晶 BaTiO₃ 構造では、理想立方晶ペロブスカイト構造からの小さな正方晶歪みが観測されている。
また、ソフトモード研究では、BaTiO₃ の相転移が格子振動の不安定性と深く関係することが示されている。
さらに、第一原理研究では、Ti 3d 軌道と O 2p 軌道の混成が強誘電性の安定化に重要であると示されている。

したがって、本 OpenMX 計算で得られた Ti-O 相対変位と酸素八面体の非対称性は、
BaTiO₃ の強誘電構造として妥当な結果である。

機械学習ポテンシャル結果の評価
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

FairChem と SevenNet は、正方晶強誘電構造を定性的によく再現した。
どちらも OpenMX と同様に、Ti-O 非対称性を持つ極性構造を与える。
ただし、OpenMX と比べると酸素変位がやや大きく、apical Ti-O 結合差を過大評価する傾向がある。

CHGNet は、z 方向のみを緩和する入力設定により正方晶的な面内配置を保持できた。
しかし、Ba 基準の内部変位を見ると、Ti 変位は OpenMX より小さく、O 変位は OpenMX より大きい。
そのため、CHGNet は対称性保持には有効であるが、
OpenMX の内部変位を定量的に再現するには不十分である。

本例における機械学習ポテンシャルの結果は、以下のように整理できる。

.. code-block:: text

   FairChem  : OpenMX に最も近い傾向を示す
   SevenNet  : FairChem に近く、良好な再現性を示す
   CHGNet    : z方向拘束により正方晶性は保持できるが、酸素変位を過大評価する

最終判断
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

本計算例では、OpenMX を正方晶 BaTiO₃ の固定格子構造最適化における DFT 基準として用いる。
OpenMX は、Ti の強誘電変位を保持し、酸素副格子を適度に緩和することで、
既往の実験構造、ソフトモード描像、および第一原理研究と整合する構造を与えた。

FairChem と SevenNet は、機械学習ポテンシャルとしては良好であり、
正方晶強誘電構造を高速に予測する用途に適している。
ただし、酸素八面体の極性歪みをやや過大評価するため、定量的な議論には OpenMX などの
密度汎関数理論計算による確認が望ましい。

CHGNet は、z 方向拘束を導入した入力により正方晶的な面内配置を保持できるが、
本構造における OpenMX 内部変位との一致度は FairChem や SevenNet より低い。
したがって、本例では、CHGNet は正方晶性を保持した補正済みの結果として扱うが、
BaTiO₃ の正方晶強誘電構造を定量的に評価する主結果としては慎重に扱う必要がある。

参考文献
----------------------------------------------------------------------

* :sup:`[1]` Megaw, H. D.,
  "Crystal Structure of Barium Titanate,"
  *Nature*, **155**, 484--485, 1945.
  `https://doi.org/10.1038/155484a0 <https://doi.org/10.1038/155484a0>`_

* :sup:`[2]` Harada, J.; Axe, J. D.; Shirane, G.,
  "Neutron-Scattering Study of Soft Modes in Cubic BaTiO₃,"
  *Physical Review B*, **4**, 155--162, 1971.
  `https://doi.org/10.1103/PhysRevB.4.155 <https://doi.org/10.1103/PhysRevB.4.155>`_

* :sup:`[3]` Cohen, R. E.,
  "Origin of Ferroelectricity in Perovskite Oxides,"
  *Nature*, **358**, 136--138, 1992.
  `https://doi.org/10.1038/358136a0 <https://doi.org/10.1038/358136a0>`_
