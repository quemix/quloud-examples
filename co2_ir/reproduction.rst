==============================
計算条件と再現手順
==============================

このページでは、 :doc:`ir_spectrum` の計算をQuloudで再現する手順と、Quloudからダウンロードした出力ファイルから記事の数値と図を作る解析スクリプトをまとめます。\
画面の操作は `Quloudオンラインマニュアル <https://manual.quloud-platform.quemix.com/>`__ （Ver.7.0）に沿って説明します。

計算環境
========

記事の計算は、2026年10月に、Quloudで使われているRSDFT（2026年4月版）とQuloudのジョブと同じ実行スクリプトをDockerに入れ、Quloudの外で実行したものです。\
CPMD、構造最適化、調和振動数の静的計算はWSL2（Intel Core Ultra 5 225U、MPI 4並列）で行いました。\
BOMDと、静的計算の確認（小さい変位、分子の平行移動）は、同じDockerイメージをAWS EC2のr8a.8xlarge（AMD EPYC 9R45）に移して行いました（MPI 8並列、BOMDはOpenMPの2スレッドを併用）。\
20ステップのBOMDの試験で、2つの環境の保存量の変化とSCFの反復回数が一致することを確かめています。

計算の条件は、以下の「Quloudでの計算手順」で示す画面の設定と同じです。\
ただし、次の2点が異なります。

* 双極子を出力する ``MDDIPOLE`` に加えて、座標を毎ステップ別のファイルに書き出す ``ALLTRAJ 1`` も指定しました。解析には使っていません。
* Quloudの画面から作る入力ファイルには、スメアリングの種類を指定する ``MPVER 0`` 、 ``KINTEG 0`` が書き込まれますが、記事の計算ではRSDFTの既定値（ ``KINTEG 1`` ）を使いました。CO₂のHOMO–LUMOギャップ（8.0 eV）は電子温度（0.03 eV）よりずっと大きく、どちらの方法でも占有数は0か2になるので、結果は変わりません。

各計算の所要時間は、構造最適化が数分、静的計算が1点あたり1分程度、CPMDが1本あたり約1時間（WSL2）、BOMDが1本あたり45〜50分（EC2）でした。

配布ファイル
============

構造ファイル
------------

Quloudの「ファイルアップロード」でMaterialとして登録する構造です。\
いずれも1辺10.6 Åの立方体セルの中に、 :math:`z` 軸に沿ったCO₂分子を1個置いたCIFファイルです。

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - ファイル
     - 内容
   * - :download:`co2_initial.cif <structures/co2_initial.cif>`
     - 構造最適化の初期構造（C–O 1.16 Å）
   * - :download:`co2_start_optimized.cif <structures/co2_start_optimized.cif>`
     - 構造最適化の結果（C–O 1.1645 Å）。最適化構造から始めるMDに使います
   * - :download:`co2_start_1150.cif <structures/co2_start_1150.cif>`
     - 両方のC–O結合を1.150 Åに縮めた構造。 :numref:`{number}節 <sec-co2-shifted-start>` のMDに使います
   * - :download:`co2_static_standard.zip <structures/co2_static_standard.zip>`
     - 調和振動数を求める静的計算の13個の構造（基準構造と、各モードに沿って0.02〜0.06 bohr動かした構造）
   * - :download:`co2_static_small.zip <structures/co2_static_small.zip>`
     - 変位を0.0025〜0.01 bohrにした13個の構造（数値誤差の確認用）
   * - :download:`co2_static_shift.zip <structures/co2_static_shift.zip>`
     - 分子全体を :math:`x` 方向に格子間隔の1/8ずつ平行移動させた9個の構造（数値誤差の確認用）

静的計算の構造のファイル名は ``co2_<モード>_<変位>.cif`` です。\
変位 :math:`u` は酸素原子の変位（bohr）で、逆対称伸縮（ ``nu3`` ）と変角（ ``nu2`` ）では、重心が動かないよう炭素原子を :math:`-2m_\mathrm{O}u/m_\mathrm{C}` だけ動かしています。\
基準構造（ ``ref`` ）は、最適化構造の炭素原子をセルの中心に、2つの酸素原子をその両側に対称に置き直したものです。

スクリプト
----------

* :download:`analyze_co2_ir.py <scripts/analyze_co2_ir.py>` : Quloudからダウンロードした出力ファイルのZIPを読み、記事中の数値を表示して、図を作成します。
* :download:`make_static_structures.py <scripts/make_static_structures.py>` : 上の静的計算の構造ファイルを作ったスクリプトです。変位の定義を確かめたり、別の変位を試したりするときに使います。

スクリプトはPython 3、NumPy、Matplotlibで動作します。

記事の計算の出力
----------------

記事の計算の出力ファイルを、Quloudの「一括ダウンロード」で得られるZIPと同じファイル名・構成にまとめたものです。\
解析に使うファイルだけを入れています。

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - ファイル
     - 内容
   * - :download:`cpmd_start_optimized.zip <data/cpmd_start_optimized.zip>`
     - 最適化構造から始めたCPMD
   * - :download:`cpmd_start_1150.zip <data/cpmd_start_1150.zip>`
     - C–O 1.150 Åから始めたCPMD
   * - :download:`bomd_start_optimized.zip <data/bomd_start_optimized.zip>`
     - 最適化構造から始めたBOMD
   * - :download:`bomd_start_1150.zip <data/bomd_start_1150.zip>`
     - C–O 1.150 Åから始めたBOMD
   * - :download:`static_standard.zip <data/static_standard.zip>` 、 :download:`static_small.zip <data/static_small.zip>` 、 :download:`static_shift.zip <data/static_shift.zip>`
     - 静的計算。上の構造ファイルの3つのセットに対応し、1つのZIPに、ジョブごとのフォルダをまとめています

MDのZIPには ``TRAJECTORY.cif`` （毎ステップの原子配置）、 ``DIPOLE.dat`` （毎ステップの双極子モーメント）、 ``info.dat`` （毎ステップのエネルギーと温度）、 ``rsdft.json`` 、 ``rsdft.atom`` が、静的計算のフォルダには ``rsdft.json`` （全エネルギー）と ``rsdft.atom`` が入っています。

Quloudでの計算手順
==================

共通の設定
----------

すべての計算で、計算ソフトにRSDFTを選び、入力項目を次のように設定します。\
表にない項目は既定値のままです。

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - 入力項目
     - 設定値
     - 既定値との違い
   * - 交換相関汎関数
     - GGA-PBE (PBE96)
     - 既定値
   * - 擬ポテンシャルセット
     - FHI
     - 既定値
   * - k グリッド（a、b、c 軸）
     - 1、1、1
     - 変更（Γ点のみ）
   * - r グリッド（a、b、c 軸）
     - 64、64、64
     - 変更（格子間隔0.313 bohr = 0.166 Å）
   * - 電子温度 (EKBT)
     - 0.03 eV
     - 既定値
   * - SCF 収束閾値（ポテンシャル）
     - 1e-15
     - 既定値

Jobを実行するときは、「インスタンス選択」のCPU区分で **4 vCPUか8 vCPU** を選んでください。\
16 vCPU以上では、計算が「Error: Too many threads」で止まります（「計算と数値を扱う上での注意」を参照）。

Materialの登録とJobの作成・実行の操作は、マニュアルの `原子構造の登録 <https://manual.quloud-platform.quemix.com/source/jobs_and_models_atom.html>`__ 、 `計算 Job の登録 <https://manual.quloud-platform.quemix.com/source/calculation.html>`__ 、 `Job の実行 <https://manual.quloud-platform.quemix.com/source/runjob.html>`__ の章を参照してください。

1. 構造最適化
-------------

``co2_initial.cif`` を登録したMaterialで、計算機能「構造最適化」のJobを作ります。\
力の収束閾値（0.0257 eV/Å）と最適化最大ステップ数（100）は既定値のままです。\
最適化後の構造は、出力ファイルの ``rsdft.atom.out.cif`` に書き出されます。

格子間隔を変えて最適化したC–O結合長は次のとおりです。r グリッド64と72で結合長が0.0001 Åまで一致したので、64を使いました。

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - r グリッド
     - 格子間隔（bohr）
     - C–O結合長（Å）
   * - 48
     - 0.417
     - 1.1654
   * - 56
     - 0.358
     - 1.1596
   * - 64
     - 0.313
     - 1.1645
   * - 72
     - 0.278
     - 1.1645

2. 調和振動数の静的計算
-----------------------

``co2_static_standard.zip`` の13個の構造をそれぞれMaterialとして登録し、計算機能「自己無撞着電子状態計算（SCF）」のJobを作って実行します。\
数値誤差を確かめる場合は、 ``co2_static_small.zip`` （13個）と ``co2_static_shift.zip`` （9個）についても同じ計算を行います。

解析スクリプトは、各Jobの全エネルギーを2次・4次の多項式でフィットして、調和振動数を求めます。

* 4次フィット： :math:`|u|\le 0.06` bohrの全点を :math:`E = ku^2/2 + c_3u^3 + c_4u^4` でフィットします。
* 2次フィット： :math:`|u|\le 0.02` bohrの点だけを :math:`E = ku^2/2` でフィットします。

調和振動数は、得られた曲率 :math:`k` と各モードの有効質量から求めます。

3. 分子動力学
-------------

``co2_start_optimized.cif`` と ``co2_start_1150.cif`` を登録したMaterialで、計算機能「第一原理分子動力学」のJobを作ります。\
最適化構造から始める計算には、1.の結果の最終構造を「Materialとして保存」したものを使うこともできます。\
入力項目は、共通の設定に加えて次のようにします。

.. list-table::
   :header-rows: 1
   :widths: 34 33 33

   * - 入力項目
     - CPMD
     - BOMD
   * - MD法
     - CPMD (Car-Parrinello)
     - BOMD (Born-Oppenheimer)
   * - 仮想電子質量
     - 400（既定値）
     - —
   * - タイムステップ
     - 0.05 fs
     - 0.5 fs
   * - ステップ数
     - 16000
     - 1600
   * - 温度
     - 10 K
     - 10 K
   * - アンサンブル
     - NVE（ミクロカノニカル）
     - NVE（ミクロカノニカル）

アンサンブルをNVEにすると、熱浴を使わずに全エネルギーを保存するMDになります。\
温度は、初速度を与えるときの温度です。

**Jobを登録したら、実行する前に入力ファイル** ``rsdft.in`` **に次の1行を書き加えます。**

.. code-block:: text

   MDDIPOLE /

これは、毎ステップの双極子モーメントを ``DIPOLE.dat`` に書き出す指定で、現在の入力画面には対応する項目がありません。\
Status が「Registered」のJobは、Job詳細画面の「ファイル」で入力ファイルを直接編集できます（マニュアルの `Job の詳細 <https://manual.quloud-platform.quemix.com/source/jobdetail.html>`__ の章）。\
書き加えた後の ``rsdft.in`` には、MDに関係する次のキーワードが含まれます。

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - キーワード
     - 意味
   * - ``SWOPT 3``
     - 分子動力学を行う
   * - ``CPMD`` 、 ``MDEMASS 400.0``
     - Car–Parrinello法を使い、電子の仮想質量を400 a.u.とする（CPMDのみ）
   * - ``MDDT`` 、 ``MDSTEP``
     - 時間刻み（fs）とステップ数
   * - ``MDTEMP 10.0``
     - 初速度を与える温度（K）
   * - ``MDDIPOLE``
     - 毎ステップ双極子モーメントを ``DIPOLE.dat`` に出力する（書き加えた行）

NVEでは、熱浴のキーワード（ ``MDNHC`` など）は書き込まれません。\
BOMDでは、各ステップで前のステップの波動関数を初期値にしてSCFを収束させます（反復の上限は「SCF 最大反復回数」）。\
``MDDIPOLE`` を指定したMDの終了後、RSDFTは双極子のスペクトルを ``dfxi.json`` 、 ``dfyi.json`` 、 ``dfzi.json`` と、そのKramers–Kronig変換 ``dfxr.json`` などにも出力します。

4. 出力のダウンロードと解析
---------------------------

各Jobの詳細画面の「ファイル」で「出力ファイル」に切り替え、「一括ダウンロード」でZIPを取得します。\
ダウンロードしたZIPを1つのフォルダ（例えば ``downloads`` ）に集め、そのフォルダを指定して解析スクリプトを実行します。

.. code-block:: bash

   python analyze_co2_ir.py downloads

スクリプトは、フォルダの中のZIPを1つずつ開き、出力ファイルの内容から計算の種類を判定します。

* ``TRAJECTORY.cif`` 、 ``info.dat`` 、 ``DIPOLE.dat`` があればMDです。 ``info.dat`` の列数からCPMDかBOMDかを、 ``TRAJECTORY.cif`` の最初のフレームのC–O結合長から開始構造を判定します。 ``DIPOLE.dat`` がない場合は、 ``MDDIPOLE`` の追記を忘れたものとして読み飛ばします。
* それ以外は静的計算です。 ``rsdft.atom`` の原子配置を基準構造と比べて、モードと変位を判定し、 ``rsdft.json`` から全エネルギーを読みます。

ZIPの名前は判定に使わないので、ダウンロードしたままの名前で構いません。\
展開したフォルダを指定することもできます。\
判定の結果を最初に表示し、続いて記事中の数値を表示して、図を ``figures`` フォルダに書き出します（ ``--figures`` で変更できます）。\
一部の計算だけを行った場合は、そのJobから求められる数値と図だけを出力します。

記事の数値と図は、上の「記事の計算の出力」のZIPを1つのフォルダに集めて、同じように実行すると得られます。

.. code-block:: bash

   python analyze_co2_ir.py data

出力の ``rsdft.atom`` は、RSDFTが分率座標を小数6桁で書き直したもので、MDでは最後のステップの構造になっています。\
そのため、スクリプトはMDの開始構造を ``TRAJECTORY.cif`` の最初のフレームから読みます。\
静的計算の変位は、構造ファイルを0.0001 bohr単位で作ってあるので、 ``rsdft.atom`` から読んだ値をその単位に丸めて使います。

計算と数値を扱う上での注意
==========================

* **時間刻み。** 電子の仮想質量400 a.u.と時間刻み0.1 fsの組み合わせでは、電子の仮想運動エネルギーが急に増え、約3 fsで計算が発散しました。0.05 fsでは安定で、保存量の初期値からのずれは、最適化構造から始めた計算で最大 :math:`5.8\times10^{-6}` Ha、1.150 Åから始めた計算で最大 :math:`1.3\times10^{-5}` Haでした。
* **BOMDのSCFと保存量。** BOMDでは、すべてのステップでSCFが収束しました（1ステップあたり約18回の反復）。保存量の初期値からのずれは、最適化構造から始めた計算で最大 :math:`5.3\times10^{-6}` Ha、1.150 Åから始めた計算で最大 :math:`5.4\times10^{-6}` Haでした。
* **初速度。** RSDFTは、乱数の種を固定した擬似乱数で初速度を与えます。そのため4つのMDの初速度は同じで、MPIの並列数を変えても変わりませんでした。重心の運動は取り除かれますが、角運動量は取り除かれません。
* **並列数。** RSDFTは実空間格子を空間的に分割してMPIのプロセスに割り当てます。担当領域に原子の非局所擬ポテンシャルが1つも含まれないプロセスがあると、「Error: Too many threads」というエラーで止まります（OpenMPのスレッド数が1でも起こります）。大きなセルの中央に分子を1個置いた今回の計算では、どの領域もセルの中心に接する分割（4並列の2×2×1、8並列の2×2×2）だけが使え、3並列、16並列、32並列は実行できませんでした。Quloudでは選んだvCPUの数だけMPIのプロセスを使うので、4 vCPUか8 vCPUを選びます。
* **スペクトルの計算。** 記事のパワースペクトルは、双極子から計算全体の平均値を引き、自己相関関数（偏りのある推定量）にHann窓の半分を掛けて余弦変換したものです。ピークの位置は、ゼロ埋めで細かくした波数の格子上の最大値で、分解能（約42 cm⁻¹）より細かい桁に意味はありません。RSDFTが出力する ``dfzi.json`` などは、 ``analyze_co2_ir.py`` の ``rsdft_style`` と同じ処理で、ピークの位置と高さが一致することを確認しました。
* **双極子の計算方法。** RSDFTは、計算の初めに原子の重心をセルの中心に移したと仮定し、すべての原子がセルの各面から5.6 bohrより離れている場合だけ、電子密度から双極子を求める式（ :doc:`ir_spectrum` の計算条件の節）を使います。この条件を満たさない場合は、原子の電荷（Bader電荷）を固定した点電荷の近似に切り替わり、MD中の電子密度の変化は双極子に反映されません。今回のセルでは、面に最も近い酸素原子でも4.1 Å（7.8 bohr）離れているので、条件を満たしています。
* **原子の座標の精度。** ``TRAJECTORY.cif`` の分率座標は小数6桁（セルの1辺10.6 Åに対して約10⁻⁵ Å）です。記事の計算で ``ALLTRAJ 1`` により別に出力した、より桁数の多い座標と比べても、ピークの位置と吸収強度は表示した桁まで一致しました。
* **双極子の変化率。** 質量で重みをつけた基準座標は、 :math:`z` 軸に沿った直線分子を仮定して原子の変位から求めています。分子軸が傾くとこの仮定が崩れるので、回帰には分子軸の傾きが小さい最初の400 fsだけを使いました。
