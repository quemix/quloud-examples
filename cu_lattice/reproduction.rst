==============================
計算条件と再現手順
==============================

このページでは、 :doc:`lattice_constant` の計算をQuloudで再現する手順と、Quloudからダウンロードした出力ファイルから記事の数値と図を作る解析スクリプトをまとめます。\
画面の操作は `Quloudオンラインマニュアル <https://manual.quloud-platform.quemix.com/>`__ に沿って説明します。

計算環境
========

記事の計算は、2026年11月に、Quloudで使われているQuantum ESPRESSO 7.5とQuloudのジョブと同じ実行スクリプトをDockerに入れ、Quloudの外で実行したものです。\
入力ファイルは、Quloud（Ver.7.0.2）が画面の設定値と構造ファイルから入力を作るプログラムに、以下の「Quloudでの計算手順」の設定値を渡して作りました。\
計算はWSL2（Intel Core Ultra 5 225U、MPI 4並列）で行い、記事の計算時間はこの環境での値です。

配布ファイル
============

構造ファイル
------------

Quloudの「ファイルアップロード」でMaterialとして登録する構造です。\
いずれもfccのCuの原始胞（1原子）のCIFファイルで、3辺の長さが立方晶の格子定数の :math:`1/\sqrt{2}` 、辺のなす角が60°です。\
ファイル名の数字が立方晶の格子定数（Å）です。

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - ファイル
     - 使う計算
   * - :download:`cu_fcc_a3.52.cif <structures/cu_fcc_a3.52.cif>`
     - エネルギー曲線（60 Ry）
   * - :download:`cu_fcc_a3.54.cif <structures/cu_fcc_a3.54.cif>`
     - エネルギー曲線（60 Ry）
   * - :download:`cu_fcc_a3.56.cif <structures/cu_fcc_a3.56.cif>`
     - エネルギー曲線（60 Ry）、vc-relax
   * - :download:`cu_fcc_a3.58.cif <structures/cu_fcc_a3.58.cif>`
     - エネルギー曲線（60 Ry）
   * - :download:`cu_fcc_a3.60.cif <structures/cu_fcc_a3.60.cif>`
     - エネルギー曲線（全カットオフ）
   * - :download:`cu_fcc_a3.62.cif <structures/cu_fcc_a3.62.cif>`
     - エネルギー曲線（全カットオフ）
   * - :download:`cu_fcc_a3.64.cif <structures/cu_fcc_a3.64.cif>`
     - エネルギー曲線（全カットオフ）、vc-relax
   * - :download:`cu_fcc_a3.66.cif <structures/cu_fcc_a3.66.cif>`
     - エネルギー曲線（全カットオフ）
   * - :download:`cu_fcc_a3.68.cif <structures/cu_fcc_a3.68.cif>`
     - エネルギー曲線（全カットオフ）
   * - :download:`cu_fcc_a3.70.cif <structures/cu_fcc_a3.70.cif>`
     - エネルギー曲線（60 Ry）
   * - :download:`cu_fcc_a3.72.cif <structures/cu_fcc_a3.72.cif>`
     - エネルギー曲線（60 Ry）、vc-relax
   * - :download:`cu_fcc_a3.74.cif <structures/cu_fcc_a3.74.cif>`
     - エネルギー曲線（60 Ry）
   * - :download:`cu_fcc_a3.76.cif <structures/cu_fcc_a3.76.cif>`
     - エネルギー曲線（60 Ry）

``vc-relax`` のやり直し（3.6287 Åから）は、3.56 Åから始めた ``vc-relax`` の結果の構造から始めます（後述）。

スクリプト
----------

* :download:`analyze_cu_lattice.py <scripts/analyze_cu_lattice.py>` : Quloudからダウンロードした出力ファイルのZIPを読み、記事中の数値を表示して、図を作成します。

スクリプトはPython 3、NumPy、Matplotlibで動作します。\
状態方程式の当てはめもNumPyだけで行います。

記事の計算の出力
----------------

記事の計算の出力ファイルを、Quloudの「一括ダウンロード」で得られるファイル名にそろえ、1つのZIPに、ジョブごとのフォルダをまとめたものです。\
各フォルダには、解析に使う ``QuloudJob.scf.out`` （pw.xの出力）と、入力のコピー ``QuloudJob.scf.in`` 、終了状態の ``QuloudJob.exit_status.json`` だけを入れています。

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - ファイル
     - 内容
   * - :download:`cu_eos_60ry.zip <data/cu_eos_60ry.zip>`
     - エネルギー曲線、60 Ry（13件）
   * - :download:`cu_eos_cutoff.zip <data/cu_eos_cutoff.zip>`
     - エネルギー曲線、40〜120 Ry（20件）
   * - :download:`cu_vcrelax.zip <data/cu_vcrelax.zip>`
     - vc-relax（8件）

* ``cu_eos_60ry.zip`` ：3.52〜3.76 Åの0.02 Å刻み13点。
* ``cu_eos_cutoff.zip`` ：40、80、100、120 Ryのそれぞれで、3.60〜3.68 Åの5点。
* ``cu_vcrelax.zip`` ：3.64 Åから40〜120 Ryの5件、60 Ryで3.56 Åと3.72 Åからの2件と、3.6287 Åからのやり直し1件。

フォルダ名（例： ``cu_scf_a3.64_ec60`` 、 ``cu_vcrelax_from3.64_ec60`` ）は内容を示すために付けたもので、解析スクリプトは使いません。

Quloudでの計算手順
==================

共通の設定
----------

すべての計算で、計算ソフトにQuantum ESPRESSOを選びます。\
入力項目は次のように設定します。表にない項目は既定値のままです。

.. list-table::
   :header-rows: 1
   :widths: 36 34 30

   * - 入力項目
     - 設定値
     - 既定値との違い
   * - 交換相関汎関数
     - GGA-PBE
     - 既定値
   * - 擬ポテンシャル（Cu）
     - ``Cu.pbe-dn-kjpaw_psl.1.0.0.UPF``
     - 一覧から選ぶ
   * - k グリッド（a、b、c 軸）
     - 24、24、24
     - 変更（既定値は4）
   * - k グリッドオフセット（a、b、c 軸）
     - オフ
     - 既定値
   * - 対称性利用
     - オン
     - **変更**
   * - 電子占有数スメアリング
     - MV
     - 変更（既定値はGaussian）
   * - スメアリング幅
     - 0.02 Ry
     - 変更（既定値は0.01 Ry）
   * - 平面波カットオフエネルギー
     - 60 Ry
     - 変更
   * - 密度・ポテンシャルカットオフエネルギー
     - 600 Ry
     - 変更
   * - SCF 収束閾値（エネルギー）
     - 1e-12 Ry
     - 変更（既定値は1e-6 Ry）

カットオフの比較では、平面波カットオフエネルギーを40、80、100、120 Ryに、密度・ポテンシャルカットオフエネルギーをその10倍（400、800、1000、1200 Ry）にします。\
**「対称性利用」は既定値がオフです。** オフのままでは結晶の対称性で既約k点に減らす処理が行われず、計算時間が大きく増えます（ :doc:`../kpoints/reproduction` ）。

Materialの登録とJobの作成・実行の操作は、マニュアルの `原子構造の登録 <https://manual.quloud-platform.quemix.com/source/jobs_and_models_atom.html>`__ 、 `計算 Job の登録 <https://manual.quloud-platform.quemix.com/source/calculation.html>`__ 、 `Job の実行 <https://manual.quloud-platform.quemix.com/source/runjob.html>`__ の章を参照してください。

1. エネルギー曲線（SCF計算）
----------------------------

計算機能「自己無撞着電子状態計算（SCF）」で、構造ファイルごとにJobを作り、実行します。\
Quloudは、3辺が等しく角が60°のセルを、QEの入力で ``ibrav = 2`` （fcc）、 ``A`` = 立方晶の格子定数（Å）として書きます。\
3.64 Å・60 RyのJobの入力ファイル ``QuloudJob.scf.in`` は、k点メッシュが24×24×24であることを除いて、 :doc:`../kpoints/reproduction` に示したものと同じです。\
1件の計算時間は、60 Ryで約20秒、120 Ryで約2.5分です。

2. 格子定数最適化（vc-relax）
-----------------------------

計算機能「格子定数最適化」で、共通の設定に加えて次の項目を設定します。

.. list-table::
   :header-rows: 1
   :widths: 36 34 30

   * - 入力項目
     - 設定値
     - 既定値との違い
   * - 応力の収束閾値
     - 0.01 GPa
     - **変更** （既定値は0.5 GPa）
   * - 目標圧力
     - 0 GPa
     - 既定値
   * - 最適化最大ステップ数
     - 100
     - 既定値
   * - 力の収束閾値
     - 0.05 eV/Å
     - 既定値

**応力の収束閾値の既定値0.5 GPa（5 kbar）は、この記事の目的には粗すぎます。** 圧力1 kbarは格子定数の約0.001 Åに相当するので、5 kbarでは0.005 Å程度の誤差が残りえます。\
1原子のfccの原始胞では、対称性により原子に力ははたらかないので、力の収束閾値は結果に影響しません。

3.64 Å・60 RyのJobの入力ファイルは次のようになります。

.. code-block:: text

   &control
    calculation = 'vc-relax'
    prefix = 'QuloudJob'
    tstress = .true.
    tprnfor = .true.
    pseudo_dir = './'
    outdir = './work'
    verbosity = 'high'
    nstep = 100
    forc_conv_thr = 0.00194463
   /
   &system
    nat = 1
    ntyp = 1
    ibrav = 2
    A = 3.639999995023336
    ecutwfc = 60.0
    ecutrho = 600.0
    occupations = 'smearing'
    smearing = 'marzari-vanderbilt'
    degauss = 0.020000
   /
   &electrons
    electron_maxstep = 100
    conv_thr = 1.00e-12
    diagonalization = 'david'
   /
   &ions
    ion_dynamics = 'bfgs'
   /
   &cell
    cell_dynamics = 'bfgs'
    press_conv_thr = 0.1000
    press = 0.0000
   /
   ATOMIC_SPECIES
   Cu 63.546 Cu.pbe-dn-kjpaw_psl.1.0.0.UPF
   ATOMIC_POSITIONS {crystal}
   Cu 0.0 0.0 0.0
   K_POINTS automatic
   24 24 24 0 0 0

QEの ``press_conv_thr`` の単位はkbarなので、0.01 GPaは ``0.1000`` と書かれます。\
出力ファイル ``QuloudJob.scf.out`` の最後の ``Begin final coordinates`` から ``End final coordinates`` の間に最適化後のセルが、その後の ``The G-vectors are recalculated for the final unit cell`` に続くSCF計算の ``P=`` に、平面波を選び直したときの圧力が書かれます。\
1件の計算時間は、60 Ryで約2〜7分、120 Ryで約8分です。

記事のやり直しの計算（3.6287 Åから）は、3.56 Åから始めたJobの最適化後の格子定数（ ``Begin final coordinates`` の後の ``CELL_PARAMETERS`` から求めた値）で原始胞のCIFを作り、同じ設定で実行したものです。\
立方晶の格子定数 :math:`a` は、 ``CELL_PARAMETERS (alat= ...)`` の ``alat`` （bohr）と、1行目の最初の成分 :math:`x` から :math:`a = 2|x|\times\mathrm{alat}\times0.529177` Åで求まります。

3. 出力のダウンロードと解析
---------------------------

各Jobの詳細画面の「ファイル」で「出力ファイル」に切り替え、「一括ダウンロード」でZIPを取得します。\
ダウンロードしたZIPを1つのフォルダ（例えば ``downloads`` ）に集め、そのフォルダを指定して解析スクリプトを実行します。

.. code-block:: bash

   python analyze_cu_lattice.py downloads

スクリプトは、フォルダの中のZIPを1つずつ開き、pw.xの出力（ ``Program PWSCF`` を含むファイル）と、同じフォルダにある入力のコピー（ ``K_POINTS`` を含むファイル）から、次の内容を読み取ってJobを判定します。

* 計算の種類（入力の ``calculation`` が ``'scf'`` か ``'vc-relax'`` か）
* 格子定数（出力の ``lattice parameter (alat)`` 。 ``ibrav = 2`` の場合は立方晶の格子定数。 ``vc-relax`` では開始時の値）
* カットオフエネルギー（出力の ``kinetic-energy cutoff`` ）

ZIPの名前やファイル名は判定に使わないので、ダウンロードしたままの名前で構いません。\
展開したフォルダを指定することもできます。\
同じ条件のJobが複数あるときは、最初の1つだけを使います。\
判定の結果を最初に表示し、続いて記事中の数値を表示して、図を ``figures`` フォルダに書き出します（ ``--figures`` で変更できます）。\
一部の計算だけを行った場合は、そのJobから求められる数値と図だけを出力します。

記事の数値と図は、上の「記事の計算の出力」のZIPを1つのフォルダに集めて、同じように実行すると得られます。

.. code-block:: bash

   python analyze_cu_lattice.py data

Jobの数を減らして試す場合は、例えば60 Ryのエネルギー曲線のうち3.58〜3.70 Åの7点と、3.64 Åからの ``vc-relax`` をQuloudで計算し、配布した出力の同じ条件の値と全エネルギー・圧力が一致することを確かめてから、残りは配布した出力で解析する、という進め方ができます。\
7点でも、Birch–Murnaghanの式の格子定数は13点の場合と同じ3.6303 Åになります（ :numref:`tab-cl-eos` ）。

計算と数値を扱う上での注意
==========================

* **SCFの収束閾値と圧力。** 圧力（応力）は全エネルギーより収束が遅く、SCF収束閾値を1e-9 Ryにすると、Cuの圧力が計算の設定によって約1 kbarばらつきます（ :doc:`../kpoints/reproduction` ）。圧力を比べる計算では、閾値を1e-12 Ryにしてください。
* **QuloudのバージョンとSCFの入力。** QuloudのVer.7.0.2より前のバージョンでは、fccの原始胞を ``ibrav = 5`` （菱面体晶）として書きます。全エネルギーは同じですが、解析スクリプトは ``ibrav = 2`` の出力だけを読みます。
* **エネルギーの単位。** 全エネルギーはRy、体積弾性率は1 Ry/Å\ :sup:`3` = 2179.87 GPaで換算しています。
* **計算時間。** 記事の時間は、WSL2のMPI 4並列で、QEの出力の最後の ``PWSCF`` の行の経過時間（WALL）です。Quloudで実行すると、選んだインスタンスによって変わります。
