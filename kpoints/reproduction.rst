==============================
計算条件と再現手順
==============================

このページでは、 :doc:`kpoint_convergence` の計算をQuloudで再現する手順と、Quloudからダウンロードした出力ファイルから記事の数値と図を作る解析スクリプトをまとめます。\
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
いずれも原始胞のCIFファイルで、3辺の長さが立方晶の格子定数の :math:`1/\sqrt{2}` 、辺のなす角が60°です。

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - ファイル
     - 内容
   * - :download:`cu_fcc_a3.60.cif <structures/cu_fcc_a3.60.cif>`
     - Cu、格子定数3.60 Å
   * - :download:`cu_fcc_a3.64.cif <structures/cu_fcc_a3.64.cif>`
     - Cu、格子定数3.64 Å
   * - :download:`cu_fcc_a3.68.cif <structures/cu_fcc_a3.68.cif>`
     - Cu、格子定数3.68 Å
   * - :download:`si_diamond_a5.42.cif <structures/si_diamond_a5.42.cif>`
     - Si、格子定数5.42 Å
   * - :download:`si_diamond_a5.47.cif <structures/si_diamond_a5.47.cif>`
     - Si、格子定数5.47 Å
   * - :download:`si_diamond_a5.52.cif <structures/si_diamond_a5.52.cif>`
     - Si、格子定数5.52 Å

Cuはfccの原始胞（1原子）、Siはダイヤモンド構造の原始胞（2原子、分率座標 (0, 0, 0) と (1/4, 1/4, 1/4)）です。

スクリプト
----------

* :download:`analyze_kpoints.py <scripts/analyze_kpoints.py>` : Quloudからダウンロードした出力ファイルのZIPを読み、記事中の数値を表示して、図を作成します。

スクリプトはPython 3、NumPy、Matplotlibで動作します。

記事の計算の出力
----------------

記事の計算の出力ファイルを、Quloudの「一括ダウンロード」で得られるファイル名にそろえ、1つのZIPに、ジョブごとのフォルダをまとめたものです。\
各フォルダには、解析に使う ``QuloudJob.scf.out`` （pw.xの出力）と、入力のコピー ``QuloudJob.scf.in`` 、終了状態の ``QuloudJob.exit_status.json`` だけを入れています。

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - ファイル
     - 内容
   * - :download:`cu_kmesh.zip <data/cu_kmesh.zip>`
     - Cu、MV 0.02 Ry（32件）
   * - :download:`cu_smearing.zip <data/cu_smearing.zip>`
     - Cu 3.64 Å、MV 0.005、0.01、0.04 Ry（23件）
   * - :download:`cu_tetrahedra.zip <data/cu_tetrahedra.zip>`
     - Cu、テトラヘドロン法（52件）
   * - :download:`si_kmesh.zip <data/si_kmesh.zip>`
     - Si、固定占有（24件）

* ``cu_kmesh.zip`` ：3.60、3.68 Åは :math:`n` = 4、6、8、10、12、14、16、20、24、32、3.64 Åはこれに40、48を加えたメッシュ。
* ``cu_smearing.zip`` ： :math:`n` = 8、12、16、20、24、32、40（0.005、0.01 Ryは48も）。
* ``cu_tetrahedra.zip`` ：Blöchlの方法と最適化テトラヘドロン法のそれぞれで、3つの格子定数 × :math:`n` = 8、10、12、14、16、20、24、32（3.64 Åは40、48も）。
* ``si_kmesh.zip`` ：3つの格子定数 × :math:`n` = 2、3、4、6、8、10、12、16。

フォルダ名（例： ``cu_a3.64_k24_sm0.020`` 、 ``cu_a3.64_k24_tetra_opt`` ）は内容を示すために付けたもので、解析スクリプトは使いません。

Quloudでの計算手順
==================

共通の設定
----------

すべての計算で、計算ソフトにQuantum ESPRESSOを選び、計算機能「自己無撞着電子状態計算（SCF）」のJobを作ります。\
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
   * - 擬ポテンシャル（Si）
     - ``Si.pbe-n-kjpaw_psl.1.0.0.UPF``
     - 一覧から選ぶ
   * - k グリッド（a、b、c 軸）
     - :math:`n` 、 :math:`n` 、 :math:`n`
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

k グリッドの :math:`n` には、調べるメッシュの分割数を入れます。\
Cuのスメアリング幅の比較では、スメアリング幅を0.005、0.01、0.04 Ryにします。

**「対称性利用」は既定値がオフです。** オフのままでは、QEの入力に ``nosym = .true.`` が書かれ、結晶の対称性で既約k点に減らす処理が行われません（ :doc:`kpoint_convergence` の :numref:`{number}節 <sec-kp-irreducible>` ）。\
計算時間が増えるほか、記事の既約k点の数と比べられなくなります。

Materialの登録とJobの作成・実行の操作は、マニュアルの `原子構造の登録 <https://manual.quloud-platform.quemix.com/source/jobs_and_models_atom.html>`__ 、 `計算 Job の登録 <https://manual.quloud-platform.quemix.com/source/calculation.html>`__ 、 `Job の実行 <https://manual.quloud-platform.quemix.com/source/runjob.html>`__ の章を参照してください。

1. Cuの計算
-----------

``cu_fcc_a3.64.cif`` などを登録したMaterialで、上の設定のJobを作り、実行します。\
k グリッドを変えたJobを、調べたいメッシュの数だけ作ります。\
Quloudは、3辺が等しく角が60°のセルを、QEの入力で ``ibrav = 2`` （fcc）、 ``A`` = 立方晶の格子定数（Å）として書きます。\
例えば、3.64 Å、 :math:`12^3` のJobの入力ファイル ``QuloudJob.scf.in`` は次のようになります。

.. code-block:: text

   &control
    calculation = 'scf'
    prefix = 'QuloudJob'
    tstress = .true.
    tprnfor = .true.
    pseudo_dir = './'
    outdir = './work'
    verbosity = 'high'
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
   ATOMIC_SPECIES
   Cu 63.546 Cu.pbe-dn-kjpaw_psl.1.0.0.UPF
   ATOMIC_POSITIONS {crystal}
   Cu 0.0 0.0 0.0
   K_POINTS automatic
   12 12 12 0 0 0

``tstress = .true.`` により、出力に応力と圧力（ ``P=`` ）が書かれます。\
``verbosity = 'high'`` により、既約k点の座標と重みの一覧が出力に書かれます（記事の :numref:`tab-kp-irreducible-4` ）。

2. Siの計算（固定占有）
-----------------------

``si_diamond_a5.47.cif`` などを登録したMaterialで、Cuと同じ設定のJobを作ります。\
「電子占有数スメアリング」の選択肢には「なし（固定占有）」がなく、どれかを選ぶと入力にスメアリングの行が書き込まれます。\
Siは固定占有で計算するので、 **Jobを登録したら、実行する前に入力ファイル** ``QuloudJob.scf.in`` **から次の3行を削除します。**

.. code-block:: text

    occupations = 'smearing'
    smearing = 'marzari-vanderbilt'
    degauss = 0.020000

3行を削除すると、QEは既定の固定占有（ ``occupations = 'fixed'`` ）で計算します。\
Status が「Registered」のJobは、Job詳細画面の「ファイル」で入力ファイルを直接編集できます（マニュアルの `Job の詳細 <https://manual.quloud-platform.quemix.com/source/jobdetail.html>`__ の章）。\
3行を残したまま（MVスメアリング0.02 Ry）計算すると、格子定数5.469 Å・ :math:`8^3` の確認計算で、全エネルギーが固定占有より約1.5 mRy高く、圧力が約1.2 kbar大きくなりました。

3. Cuのテトラヘドロン法
-----------------------

Cuの計算と同じ設定のJobを作ります。\
「電子占有数スメアリング」の選択肢にはテトラヘドロン法がないので、Siと同じく、 **Jobを登録したら、実行する前に入力ファイル** ``QuloudJob.scf.in`` **の次の3行を書き換えます。**

.. code-block:: text

    occupations = 'smearing'
    smearing = 'marzari-vanderbilt'
    degauss = 0.020000

この3行を、Blöchlの方法なら次の1行に、

.. code-block:: text

    occupations = 'tetrahedra'

最適化テトラヘドロン法なら次の1行にします。

.. code-block:: text

    occupations = 'tetrahedra_opt'

テトラヘドロン法は、 ``K_POINTS automatic`` で指定した規則的なメッシュでしか使えません。Quloudの「k グリッド」はこの形式で書かれるので、そのままで構いません。\
出力には、応力の計算を推奨しないという警告（ ``BEWARE: stress calculation with tetrahedra (not recommanded)`` ）が書かれますが、計算は最後まで行われます（記事の :numref:`{number}節 <sec-kp-tetra>` ）。\
テトラヘドロン法は細かいメッシュで時間がかかり、 :math:`48^3` ではMPI 4並列で約9分でした（MVスメアリングでは約2分）。

4. 出力のダウンロードと解析
---------------------------

各Jobの詳細画面の「ファイル」で「出力ファイル」に切り替え、「一括ダウンロード」でZIPを取得します。\
ダウンロードしたZIPを1つのフォルダ（例えば ``downloads`` ）に集め、そのフォルダを指定して解析スクリプトを実行します。

.. code-block:: bash

   python analyze_kpoints.py downloads

スクリプトは、フォルダの中のZIPを1つずつ開き、pw.xの出力（ ``Program PWSCF`` を含むファイル）と、同じフォルダにある入力のコピー（ ``K_POINTS`` を含むファイル）から、次の内容を読み取ってJobを判定します。

* 元素と原子数、格子定数（出力の ``lattice parameter (alat)`` 。 ``ibrav = 2`` の場合は立方晶の格子定数）
* k点メッシュ :math:`n` （入力の ``K_POINTS automatic`` の行）
* 占有数（出力にテトラヘドロン法を使った旨が書かれていればその種類、スメアリングの幅が書かれていればその幅、どちらもなければ固定占有）

ZIPの名前やファイル名は判定に使わないので、ダウンロードしたままの名前で構いません。\
展開したフォルダを指定することもできます。\
同じ条件のJobが複数あるときは、最初の1つだけを使います。\
判定の結果を最初に表示し、続いて記事中の数値（表と、許容誤差に収まるメッシュ）を表示して、図を ``figures`` フォルダに書き出します（ ``--figures`` で変更できます）。\
一部の計算だけを行った場合は、そのJobから求められる数値と図だけを出力します。\
参照値には、そのJobの系列で最も細かいメッシュの値を使うので、記事より粗いメッシュまでしか計算していない場合は、数値が記事と変わります。

記事の数値と図は、上の「記事の計算の出力」のZIPを1つのフォルダに集めて、同じように実行すると得られます。

.. code-block:: bash

   python analyze_kpoints.py data

Jobの数を減らして試す場合は、例えばCu 3.64 Å（ :math:`n` = 8、12、16、24）とSi 5.47 Å（ :math:`n` = 4、6、8）をQuloudで計算し、配布した出力の同じ条件の値と全エネルギー・圧力が一致することを確かめてから、残りは配布した出力で解析する、という進め方ができます。

計算と数値を扱う上での注意
==========================

* **SCFの収束閾値と圧力。** Cu 3.64 Å・ :math:`12^3` で、SCF 収束閾値を1e-9 Ryにすると、圧力は計算の設定（対称性の使い方、電荷密度の混合の割合）によって −11.27〜−12.35 kbarとばらつきました。1e-12 Ryでは、どの設定でも −12.05±0.02 kbarにそろいました。全エネルギーは1e-9 Ryでも8桁まで一致します。圧力を比べる計算では、閾値を厳しくしてください。
* **対称性と既約k点。** 記事の計算では、すべてのJobでQEが48個の対称操作を見つけました（出力の ``48 Sym. Ops.`` ）。QuloudのVer.7.0.2より前のバージョンでは、fccの原始胞を ``ibrav = 5`` （菱面体晶）として書くため、QEは12個の対称操作しか使わず、既約k点が多くなります（Cu :math:`12^3` で189点。Ver.7.0.2以降は72点）。全エネルギーは :math:`10^{-8}` Ryの桁まで同じです。解析スクリプトは ``ibrav = 2`` の出力だけを読みます。
* **参照値。** 全エネルギーの収束は、最も細かいメッシュ（Cu :math:`48^3` 、Si :math:`16^3` ）の値との差で評価しています。参照値自体の誤差は、Cuの :math:`40^3` と :math:`48^3` の差（0.003 meV/atom、0.01 kbar）、Siの :math:`12^3` と :math:`16^3` の差（0.07 meV/atom）程度です。スメアリング幅0.005 Ryの計算は、 :math:`48^3` でもまだ0.08 meV/atom、0.2 kbar程度動いています。
* **計算時間。** 記事の時間は、WSL2のMPI 4並列で、QEの出力の最後の ``PWSCF`` の行の経過時間（WALL）です。Quloudで実行すると、選んだインスタンスによって変わります。
