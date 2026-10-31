==============================
計算条件と再現手順
==============================

このページでは、 :doc:`ir_spectrum` の数値と図を得た計算の条件、入力ファイル、数値データ、および再実行の手順をまとめます。

計算環境
========

CPMD、構造最適化、調和振動数の静的計算は、2026年10月に、WSL2上のDockerで行いました（Intel Core Ultra 5 225U、MPI 4並列）。\
BOMDと、静的計算の確認（小さい変位、分子の平行移動）は、同じDockerイメージをAWS EC2のr8a.8xlarge（AMD EPYC 9R45、32コア）に移して行いました（MPI 8並列、BOMDはOpenMP 2スレッドを併用）。\
20ステップのBOMDの試験で、2つの環境の保存量の変化とSCFの反復回数が一致することを確かめています。\
使用したのは、Quloudで使われているRSDFT（2026年4月版）をビルドしたローカル用のDockerイメージです。\
Quloud上では実行していません。\
このイメージは公開していないため、以下ではRSDFTを実行できる環境があるものとして手順を示します。

RSDFTは、作業ディレクトリの ``rsdft.in`` （計算条件）と ``rsdft.atom`` （CIF形式の原子配置）を読み込みます。\
各計算の所要時間は、構造最適化が数分、静的計算が1点あたり1分程度、CPMDが1本あたり約1時間（WSL2）、BOMDが1本あたり45〜50分（EC2）でした。

全計算に共通する条件は次のとおりです。

* 交換相関汎関数PBE（ ``XCTYPE GGA_PBE96`` ）、FHI形式の擬ポテンシャル（ ``PSSET FHI`` ）
* 1辺10.6 Åの立方体セル、周期境界条件、Γ点のみ（ ``KGRID 1 1 1`` ）
* 実空間格子 :math:`64^3` 点（格子間隔0.313 bohr = 0.166 Å）
* 占有のスメアリング幅 ``EKBT`` = 0.0011 Ha（0.03 eV、Quloudの既定値）
* SCF収束条件 ``SCFCONV 1e-15``

配布ファイル
============

入力ファイル
------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - ファイル
     - 内容
   * - :download:`opt/rsdft.in <inputs/opt/rsdft.in>` 、 :download:`opt/rsdft.atom <inputs/opt/rsdft.atom>`
     - 構造最適化。初期構造はC–O 1.16 Å
   * - :download:`harmonic/rsdft.in <inputs/harmonic/rsdft.in>`
     - 調和振動数を求める静的計算（SCFのみ）。原子配置は下記のスクリプトで作成
   * - :download:`md_opt_start/rsdft.in <inputs/md_opt_start/rsdft.in>` 、 :download:`md_opt_start/rsdft.atom <inputs/md_opt_start/rsdft.atom>`
     - 最適化構造から始めるMD
   * - :download:`md_1150_start/rsdft.in <inputs/md_1150_start/rsdft.in>` 、 :download:`md_1150_start/rsdft.atom <inputs/md_1150_start/rsdft.atom>`
     - C–O 1.150 Åから始めるMD（ ``rsdft.in`` は上と同じ）
   * - :download:`md_bomd_opt_start/rsdft.in <inputs/md_bomd_opt_start/rsdft.in>` 、 :download:`md_bomd_opt_start/rsdft.atom <inputs/md_bomd_opt_start/rsdft.atom>`
     - 最適化構造から始めるBOMD（原子配置はCPMDと同じ）
   * - :download:`md_bomd_1150_start/rsdft.in <inputs/md_bomd_1150_start/rsdft.in>` 、 :download:`md_bomd_1150_start/rsdft.atom <inputs/md_bomd_1150_start/rsdft.atom>`
     - C–O 1.150 Åから始めるBOMD

スクリプト
----------

* :download:`make_harmonic_inputs.py <scripts/make_harmonic_inputs.py>` : 最適化構造の原子を、対称伸縮・変角・逆対称伸縮の各モードに沿って動かした13個の静的計算の入力を作成します。変位を小さくした13個の入力と、分子を平行移動させた9個の入力も作成できます。
* :download:`collect_rsdft_outputs.py <scripts/collect_rsdft_outputs.py>` : RSDFTの出力から、下記のCSVファイルを作成します。
* :download:`analyze_co2_ir.py <scripts/analyze_co2_ir.py>` : CSVファイルから、記事中の数値を表示し、すべての図を作成します。RSDFTの計算は行いません。

スクリプトはPython 3、NumPy、Matplotlibで動作します。

数値データ
----------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - ファイル
     - 内容
   * - :download:`md_start_optimized.csv.gz <data/md_start_optimized.csv.gz>`
     - 最適化構造から始めたMDの全16001ステップ。時刻（fs）、双極子モーメントの :math:`x,y,z` 成分（a.u.）、C、O1、O2の座標（Å）、保存量の初期値からのずれ（Ha）、電子の仮想運動エネルギー（Ha）、温度（K）
   * - :download:`md_start_1150.csv.gz <data/md_start_1150.csv.gz>`
     - C–O 1.150 Åから始めたMDの同上
   * - :download:`md_bomd_start_optimized.csv.gz <data/md_bomd_start_optimized.csv.gz>` 、 :download:`md_bomd_start_1150.csv.gz <data/md_bomd_start_1150.csv.gz>`
     - BOMDの全1601ステップ。列はCPMDと同じで、電子の仮想運動エネルギーの列は0
   * - :download:`harmonic_energies.csv <data/harmonic_energies.csv>`
     - 静的計算の全エネルギー（Ha）。モード名と変位 :math:`u` （bohr）ごと
   * - :download:`harmonic_small_energies.csv <data/harmonic_small_energies.csv>`
     - 変位を0.0025〜0.01 bohrにした静的計算の同上
   * - :download:`grid_shift_energies.csv <data/grid_shift_energies.csv>`
     - 分子を :math:`x` 方向に平行移動させた静的計算の全エネルギー。 ``u_bohr`` は移動量

双極子モーメントの単位は原子単位（1 a.u. = 2.5417 D）です。

計算手順
========

1. 構造最適化
-------------

``inputs/opt`` の2ファイルでRSDFTを実行します。\
``SWOPT 7`` で構造最適化を行い、原子に働く力の最大値が ``ATOMOPT1`` で指定した :math:`5\times10^{-4}` Ha/bohr（約0.026 eV/Å、Quloudの既定値）を下回るまで続けます。\
最適化後の構造は ``rsdft.atom.out.cif`` に出力されます。

格子間隔を変えて最適化したC–O結合長は次のとおりです。格子点64と72で結合長が0.0001 Åまで一致したので、格子点64を使いました。

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - ``NGRID``
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

.. code-block:: bash

   python make_harmonic_inputs.py inputs/harmonic/rsdft.in harmonic

``harmonic/<モード>_<変位>/`` に13個の入力ができます。\
基準の構造は、最適化構造の炭素原子をセルの中心に、2つの酸素原子をその両側に対称に置き直したものです。\
変位 :math:`u` は酸素原子の変位（bohr）で、逆対称伸縮と変角では、重心が動かないよう炭素原子を :math:`-2m_\mathrm{O}u/m_\mathrm{C}` だけ動かします。\
各ディレクトリでRSDFTを実行した後、全エネルギーを集めます。

.. code-block:: bash

   python collect_rsdft_outputs.py harmonic harmonic data/harmonic_energies.csv

``collect_rsdft_outputs.py`` は、各ディレクトリの ``output/rsdft.json`` を読みます。\
出力先が異なる場合は、スクリプトのパスを書き換えてください。

調和振動数は、エネルギーを :math:`E = ku^2/2 + c_3u^3 + c_4u^4` でフィットした曲率 :math:`k` と、各モードの有効質量から求めます（ ``analyze_co2_ir.py`` の ``harmonic_frequencies`` ）。\
記事中の範囲の下限は :math:`|u|\le 0.06` bohrの全点での4次フィット、上限は :math:`|u|\le 0.02` bohrの点での2次フィットの値です。

変位を小さくした計算と、分子を平行移動させた計算の入力は、3番目の引数で作ります。

.. code-block:: bash

   python make_harmonic_inputs.py inputs/harmonic/rsdft.in harmonic_small small
   python make_harmonic_inputs.py inputs/harmonic/rsdft.in grid_shift shift
   python collect_rsdft_outputs.py harmonic harmonic_small data/harmonic_small_energies.csv
   python collect_rsdft_outputs.py harmonic grid_shift data/grid_shift_energies.csv

``analyze_co2_ir.py`` の ``static_checks`` は、各点の :math:`2\Delta E/u^2` から求めた調和振動数と、平行移動による全エネルギーの変化の幅を表示します。

3. 分子動力学
-------------

``inputs/md_opt_start`` と ``inputs/md_1150_start`` （CPMD）、 ``inputs/md_bomd_opt_start`` と ``inputs/md_bomd_1150_start`` （BOMD）で、それぞれRSDFTを実行します。MDに関係するキーワードは次のとおりです。

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - キーワード
     - 意味
   * - ``SWOPT 3``
     - 分子動力学を行う
   * - ``CPMD``
     - Car–Parrinello法を使う
   * - ``MDEMASS 400.0``
     - 電子の仮想質量（a.u.）。RSDFTとQuloudの既定値
   * - ``MDDT 0.05`` 、 ``MDSTEP 16000``
     - 時間刻み（fs）とステップ数（BOMDでは ``MDDT 0.5`` 、 ``MDSTEP 1600`` ）
   * - ``MDTEMP 10.0``
     - 初速度を与える温度（K）
   * - ``MDDIPOLE``
     - 毎ステップ双極子モーメントを ``DIPOLE.dat`` に出力する
   * - ``ALLTRAJ 1``
     - 毎ステップの原子の座標・速度・力を ``traj.dat`` に出力する

BOMDの入力は、CPMDの入力から ``CPMD`` と ``MDEMASS`` を除き、時間刻みとステップ数を変えたものです。\
BOMDでは、各ステップで前のステップの波動関数を初期値にしてSCFを収束させます（反復の上限は ``DITER`` ）。\
熱浴のキーワード（ ``MDNHC`` など）を指定していないので、どちらもNVE条件になります。\
``MDDIPOLE`` を指定したMDの終了後、RSDFTは双極子のスペクトルを ``dfxi.json`` 、 ``dfyi.json`` 、 ``dfzi.json`` と、そのKramers–Kronig変換 ``dfxr.json`` などに出力します。\
``analyze_co2_ir.py`` の ``rsdft_style`` は同じ処理を実装したもので、出力されたJSONとピークの位置・高さが一致することを確認しました。

MDの出力から、記事で使うCSVを作ります。

.. code-block:: bash

   python collect_rsdft_outputs.py md md_opt_start/output data/md_start_optimized.csv.gz
   python collect_rsdft_outputs.py md md_1150_start/output data/md_start_1150.csv.gz
   python collect_rsdft_outputs.py md md_bomd_opt_start/output data/md_bomd_start_optimized.csv.gz
   python collect_rsdft_outputs.py md md_bomd_1150_start/output data/md_bomd_start_1150.csv.gz

4. 数値と図の作成
-----------------

.. code-block:: bash

   python analyze_co2_ir.py

``scripts/`` と同じ階層の ``data/`` にあるCSVを読み、記事中の数値を表示して、 ``figures/`` にすべての図を出力します。

計算と数値を扱う上での注意
==========================

* **時間刻み。** 電子の仮想質量400 a.u.と時間刻み0.1 fsの組み合わせでは、電子の仮想運動エネルギーが急に増え、約3 fsで計算が発散しました。0.05 fsでは安定で、保存量の初期値からのずれは、最適化構造から始めた計算で最大 :math:`5.8\times10^{-6}` Ha、1.150 Åから始めた計算で最大 :math:`1.3\times10^{-5}` Haでした。
* **BOMDのSCFと保存量。** BOMDでは、すべてのステップでSCFが収束しました（1ステップあたり約18回の反復）。保存量の初期値からのずれは、最適化構造から始めた計算で最大 :math:`5.3\times10^{-6}` Ha、1.150 Åから始めた計算で最大 :math:`5.4\times10^{-6}` Haでした。
* **初速度。** RSDFTは、乱数の種を固定した擬似乱数で初速度を与えます。そのため4つのMDの初速度は同じです。重心の運動は取り除かれますが、角運動量は取り除かれません。
* **並列数。** RSDFTは実空間格子を空間的に分割してMPIのプロセスに割り当てます。担当領域に原子の非局所擬ポテンシャルが1つも含まれないプロセスがあると、「Error: Too many threads」というエラーで止まります（OpenMPのスレッド数が1でも起こります）。大きなセルの中央に分子を1個置いた今回の計算では、どの領域もセルの中心に接する分割（4並列の2×2×1、8並列の2×2×2）だけが使え、3並列、16並列、32並列は実行できませんでした。それ以上の計算資源は、OpenMPのスレッドで使いました。
* **スペクトルの計算。** 記事のパワースペクトルは、双極子から計算全体の平均値を引き、自己相関関数（偏りのある推定量）にHann窓の半分を掛けて余弦変換したものです。ピークの位置は、ゼロ埋めで細かくした波数の格子上の最大値で、分解能（約42 cm⁻¹）より細かい桁に意味はありません。
* **双極子の計算方法。** RSDFTは、計算の初めに原子の重心をセルの中心に移したと仮定し、すべての原子がセルの各面から5.6 bohrより離れている場合だけ、電子密度から双極子を求める式（ :doc:`ir_spectrum` の計算条件の節）を使います。この条件を満たさない場合は、原子の電荷（Bader電荷）を固定した点電荷の近似に切り替わり、MD中の電子密度の変化は双極子に反映されません。今回のセルでは、面に最も近い酸素原子でも4.1 Å（7.8 bohr）離れているので、条件を満たしています。
* **双極子の変化率。** 質量で重みをつけた基準座標は、 :math:`z` 軸に沿った直線分子を仮定して原子の変位から求めています。分子軸が傾くとこの仮定が崩れるので、回帰には分子軸の傾きが小さい最初の400 fsだけを使いました。
