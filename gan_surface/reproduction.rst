==============================
計算条件と再現手順
==============================

このページでは、 :doc:`phase_diagram` の計算をQuloudで行う手順と、Quloudからダウンロードした出力ファイルから記事の数値と図を作る解析スクリプトをまとめます。\
画面の操作は `Quloudオンラインマニュアル <https://manual.quloud-platform.quemix.com/>`__ に沿って説明します。

.. important::

   **表面スラブの計算は、現在のQuloudの画面だけでは行えません。**\
   スラブの底面を終端する擬水素（価数0.75）は、表面に吸着したH原子とは別の擬ポテンシャルを使う必要があります。\
   QuloudのQuantum ESPRESSOの設定では、擬ポテンシャルを元素ごとに1つ選ぶため、同じ構造の中でH原子を2種類に分けられません。\
   また、価数0.75の擬水素の擬ポテンシャルは、Quloudの擬ポテンシャルの一覧にありません。\
   表面・界面の計算でこの機能が必要な場合は、 `お問い合わせ <https://www.quemix.com/contact>`__ からご連絡ください。

計算環境
========

記事の計算は、Quloudと同じ計算コードを使い、Quloudの外で実行したものです。

.. list-table::
   :header-rows: 1
   :widths: 30 70
   :class: wrap-table

   * - 計算
     - 実行環境
   * - 表面スラブ（4件）
     - Quantum ESPRESSO 7.6、AWS EC2で32 MPIプロセス（2026年10月）。Quloudで使われているQuantum ESPRESSOは7.5で、版が異なります
   * - Ga原子・H₂（QE）
     - Quantum ESPRESSO 7.5。Quloudのジョブと同じ実行スクリプトを入れたDockerコンテナを、WSL2（Intel Core Ultra 5 225U、MPI 4並列）で実行（2026年10〜11月）
   * - H₂（Psi4）
     - Psi4 1.10。同じくQuloudの実行スクリプトを入れたDockerコンテナで実行（2026年11月）

QEの入力ファイルは、Quloudの入力生成プログラムを通さず、手で作りました。\
Psi4の入力ファイルは、Quloudの「振動数解析（Psi4）」が以下の設定値から作るものと同じです。

配布ファイル
============

構造ファイル
------------

Quloudの「ファイルアップロード」でMaterialとして登録する構造です。\
スラブはすべて構造最適化の前の初期構造で、 ``Hn1`` 〜 ``Hn4`` が底面の擬水素、 ``N1`` 〜 ``N4`` が底面のN原子です（この8原子を固定します）。\
CIFでは擬水素の元素記号を ``H`` と書いています。

.. list-table::
   :header-rows: 1
   :widths: 40 60
   :class: wrap-table

   * - ファイル
     - 内容
   * - :download:`gan0001_ideal.cif <structures/gan0001_ideal.cif>`
     - Ideal （44原子）
   * - :download:`gan0001_ga_adatom_t4.cif <structures/gan0001_ga_adatom_t4.cif>`
     - Ga adatom、T4サイト（45原子）。構造最適化した Ideal の上にGa原子を置いたもの
   * - :download:`gan0001_ga_adatom_h3.cif <structures/gan0001_ga_adatom_h3.cif>`
     - Ga adatom、H3サイト（45原子）。 :ref:`吸着位置の確認 <gan-site-check>` の比較用
   * - :download:`gan0001_3ga_h.cif <structures/gan0001_3ga_h.cif>`
     - 3Ga-H （47原子）
   * - :download:`ga_atom_box.cif <structures/ga_atom_box.cif>`
     - 孤立Ga原子、一辺24 bohrの立方体セル
   * - :download:`h2_box.cif <structures/h2_box.cif>`
     - H₂分子（QE用）、一辺30 bohrの立方体セル
   * - :download:`h2.xyz <structures/h2.xyz>`
     - H₂分子（Psi4用、Molecule）

擬ポテンシャル
--------------

* :download:`H_N_0.75.PBE.UPF <data/H_N_0.75.PBE.UPF>` ：底面の擬水素の擬ポテンシャル。Quantum ESPRESSO 7.5の ``ld1.x`` で次の条件で作りました。

.. list-table::
   :header-rows: 1
   :widths: 40 60
   :class: wrap-table

   * - 項目
     - 条件
   * - 原子番号・価数
     - 0.75（電子配置 1s\ :sup:`0.75` ）
   * - 交換相関汎関数
     - PBE
   * - 種類
     - ノルム保存型、Troullier–Martins、非相対論
   * - カットオフ半径
     - 0.8 bohr（s軌道のみ、局所成分 :math:`l` = 0）

それ以外の擬ポテンシャル（Ga、N、H）は、Quloudの一覧にあるpslibrary 1.0.0のものです。

スクリプト
----------

* :download:`analyze_gan_surface.py <scripts/analyze_gan_surface.py>` ：Quloudからダウンロードした出力ファイルのZIPを読み、記事中の数値を表示して、図を作成します。

スクリプトはPython 3、NumPy、Matplotlibで動作します。\
ジョブはファイル名ではなく中身で判定します（QEの入力の原子の種類と数、Psi4の出力の振動数の行）。\
Ga adatom の吸着位置（T4、H3）は、構造最適化した後の座標から判定します。

記事の計算の出力
----------------

記事の計算の出力ファイルを、Quloudの「一括ダウンロード」で得られるファイル名にそろえ、ジョブごとのフォルダを1つのZIPにまとめたものです。\
擬ポテンシャルと作業用のファイルは除いています。

.. list-table::
   :header-rows: 1
   :widths: 30 70
   :class: wrap-table

   * - ファイル
     - 内容
   * - :download:`gan_slabs.zip <data/gan_slabs.zip>`
     - 表面スラブの構造最適化（4件）： ``QuloudJob.scf.in`` （入力）と ``QuloudJob.scf.out`` （pw.xの出力）
   * - :download:`gas_qe.zip <data/gas_qe.zip>`
     - Ga原子（スピン分極あり・なし）とH₂のSCF計算（3件）
   * - :download:`h2_psi4.zip <data/h2_psi4.zip>`
     - H₂の振動数解析（Psi4、1件）： ``psi4_input_step1.in`` 、 ``psi4_input_step2.in`` と出力 ``psi4_step1.out`` 、 ``psi4_step2.out``

* 表面スラブはQuloudの外で計算したので、 ``QuloudJob.scf.out`` はpw.xの標準出力をこの名前にしたものです。終了状態のファイル ``QuloudJob.exit_status.json`` はありません。
* スピン分極なしのGa原子は、参照エネルギーには使わず、スピン分極ありとの差を示すためのものです（ :ref:`適用範囲 <gan-scope>` ）。
* フォルダ名（例： ``ga_adatom_t4`` ）は内容を示すために付けたもので、解析スクリプトは使いません。

解析の実行
----------

ダウンロードしたZIPを1つのフォルダに集め、そのフォルダを渡します。

.. code-block:: console

   $ python analyze_gan_surface.py data/ --figures figures/

吸着エネルギー、H₂の振動数と回転定数、分圧、相境界の温度を表示し、記事の4つの図（ ``models.png`` 、 ``delta_g.png`` 、 ``phase_diagram.png`` 、 ``adatom_site.png`` ）を ``figures/`` に書き出します。

Quloudでの計算手順
==================

Materialの登録とJobの作成・実行の操作は、マニュアルの `原子構造の登録 <https://manual.quloud-platform.quemix.com/source/jobs_and_models_atom.html>`__ 、 `計算 Job の登録 <https://manual.quloud-platform.quemix.com/source/calculation.html>`__ 、 `Job の実行 <https://manual.quloud-platform.quemix.com/source/runjob.html>`__ の章を参照してください。

1. H₂の振動数と回転定数（Psi4）
-------------------------------

``h2.xyz`` をMoleculeとして登録し、計算ソフトにPsi4、計算機能に「振動数解析（Psi4）」を選びます。\
この計算機能は、構造最適化の後に振動数解析を行う2段のワークフローです。\
入力項目は次のように設定します。表にない項目は既定値のままです。

.. list-table::
   :header-rows: 1
   :widths: 36 34 30

   * - 入力項目
     - 設定値
     - 既定値との違い
   * - 計算手法
     - PBE
     - 変更（既定値はB3LYP）
   * - 基底関数系
     - cc-pVTZ
     - 変更（既定値は6-31G(d,p)）
   * - スピン多重度
     - 1
     - 既定値
   * - Reference
     - RHF
     - 既定値

振動数解析の温度と圧力の欄は、Psi4が出力する熱化学量の計算にだけ使われます。\
記事では、出力 ``psi4_step2.out`` の振動数（ ``Freq [cm^-1]`` の行）と回転定数（最初の ``Rotational constants`` の行の :math:`B` ）だけを使い、化学ポテンシャルは成長条件の温度と分圧で解析スクリプトが計算します。

2. Ga原子とH₂の全エネルギー（QE）
---------------------------------

``ga_atom_box.cif`` と ``h2_box.cif`` をそれぞれMaterialとして登録し、計算ソフトにQuantum ESPRESSO、計算機能に「自己無撞着電子状態計算（QE）」を選びます。\
共通の設定は次のとおりです。

.. list-table::
   :header-rows: 1
   :widths: 40 60
   :class: wrap-table

   * - 入力項目
     - 設定値
   * - 交換相関汎関数
     - GGA-PBE
   * - 擬ポテンシャル
     - Ga ``Ga.pbe-dn-kjpaw_psl.1.0.0.UPF`` 、H ``H.pbe-kjpaw_psl.1.0.0.UPF``
   * - k グリッド（a、b、c 軸）
     - 1、1、1
   * - 平面波カットオフエネルギー
     - 70 Ry
   * - 密度・ポテンシャルカットオフエネルギー
     - 400 Ry

Ga原子はスピン分極させ、全磁化を1 :math:`\mu_\mathrm{B}` に固定して、整数の占有で計算します。\
画面にない設定なので、Jobを作った後、実行する前に入力ファイル ``QuloudJob.scf.in`` を直接編集し（Registeredの Job）、 ``&SYSTEM`` と ``&ELECTRONS`` を次のようにします。

.. code-block:: text

   &SYSTEM
     ...
     occupations = 'fixed'
     nspin = 2
     tot_magnetization = 1
     starting_magnetization(1) = 0.5
     nosym = .true.
   /
   &ELECTRONS
     conv_thr = 1.0d-6
     mixing_mode = 'local-TF'
     mixing_beta = 0.10
     mixing_ndim = 8
     electron_maxstep = 200
   /

Ga原子のp軌道は3重に縮退しており、1個の電子をどれかに入れる整数の占有ではSCFが収束しにくくなります。\
混合の係数（ ``mixing_beta`` ）を小さくし、収束閾値をQuloudの既定値の :math:`10^{-6}` Ryにしました。\
H₂は閉殻なので、 ``occupations = 'fixed'`` にするだけです。\
記事の入力は ``K_POINTS gamma`` （Γ点だけの計算）で、k グリッド1、1、1と同じk点です。\
記事で使った入力ファイルは、 ``gas_qe.zip`` の各フォルダにある ``QuloudJob.scf.in`` です。

3. 表面スラブの構造最適化（QE）
-------------------------------

計算機能「構造最適化（QE）」で、スラブの4つの構造それぞれについて計算します。\
冒頭に書いたとおり、底面の擬水素を別の種として扱う設定は、現在のQuloudではできません。\
記事の計算で使った入力ファイルの要点は次のとおりです（T4サイトの Ga adatom の例、原子の座標は省略）。\
全文は ``gan_slabs.zip`` の各フォルダにある ``QuloudJob.scf.in`` です。

.. code-block:: text

   &CONTROL
     calculation = 'relax'
     tprnfor = .true.
     forc_conv_thr = 1.0e-03
   /
   &SYSTEM
     ibrav = 0
     nat = 45
     ntyp = 3
     ecutwfc = 70.0
     ecutrho = 400.0
     input_dft = 'PBE'
     occupations = 'fixed'
   /
   &ELECTRONS
     conv_thr = 1.0e-08
     mixing_beta = 0.30
   /
   &IONS
     ion_dynamics = 'bfgs'
   /
   ATOMIC_SPECIES
   Ga    69.72300 Ga.pbe-dn-kjpaw_psl.1.0.0.UPF
   N     14.00670 N.pbe-n-kjpaw_psl.1.0.0.UPF
   Hn     1.00794 H_N_0.75.PBE.UPF

   ATOMIC_POSITIONS angstrom
   Hn        0.0000000000      0.0000000000      9.0000000000 0 0 0
   ...
   N         0.0000000000      0.0000000000     10.0000000000 0 0 0
   ...

   K_POINTS automatic
   3 3 1 0 0 0

* 底面の擬水素は種 ``Hn`` として ``H_N_0.75.PBE.UPF`` を割り当てます。 3Ga-H では、表面のH原子に種 ``H`` （ ``H.pbe-kjpaw_psl.1.0.0.UPF`` ）を加え、 ``ntyp = 4`` になります。
* 座標の後ろの ``0 0 0`` は、その原子を固定する指定です。底面の擬水素4個とN原子4個を固定します。
* Ideal だけは電子数が奇数なので、 ``occupations = 'smearing'`` 、 ``smearing = 'gaussian'`` 、 ``degauss = 0.01`` です。解析スクリプトは、スメアリングを使った出力では :math:`(F+E)/2` を全エネルギーとして使います（ :numref:`tab-gan-conditions` の注）。
* 1件の計算時間は、32 MPIプロセスで15〜31分でした（BFGSで13〜26ステップ）。
