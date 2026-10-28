==============================
計算条件と再現手順
==============================

このページでは、 :doc:`band_formation` の数値と図を得た計算の条件、スクリプト、数値データ、および再実行の手順をまとめます。

計算環境
========

計算は2026年10月に、WSL上のDockerで行いました。使用したのは、Psi4 1.10を含むRadonPy用のローカルDockerイメージ（ ``radonpy-local:v1.0-beta.1`` ）です。Quloud上では実行していません。このイメージは公開していないため、以下ではPsi4 1.10、NumPy、Matplotlibが使えるPython環境で各スクリプトを実行する形で手順を示します。他のPsi4のバージョンでの再実行は確認していません。

全計算に共通する条件は次のとおりです。

* 中性・直線・等間隔・開放端の水素鎖。原子は :math:`x` 軸上に1.8 Å間隔で配置（ ``symmetry c1`` 、 ``no_reorient`` 、 ``no_com`` ）
* 基底関数STO-3G、電荷0、スピン多重度1（ :math:`N_\alpha = N_\beta = N/2` ）
* SCF収束条件はエネルギー・密度ともに :math:`10^{-9}` 、最大500反復
* PBEの積分グリッドはPsi4の既定値（動径75点、角度302点）
* スレッド数2

配布ファイル
============

Psi4入力スクリプト
------------------

* :download:`hydrogen_chain_psi4.py <scripts/hydrogen_chain_psi4.py>` : 原子数を変えながらRHFまたはRKSを計算し、軌道エネルギーと擬似波数をCSVに出力します（DF-SCF）。
* :download:`hydrogen_chain_bond_order.py <scripts/hydrogen_chain_bond_order.py>` : RHFとRKS-PBEのLöwdin結合次数を求め、RHF解の安定性解析を行います（PK積分）。
* :download:`hydrogen_chain_spin.py <scripts/hydrogen_chain_spin.py>` : RHF、RKS-PBE、UHF、UKS-PBEを順に計算し、エネルギー、軌道ギャップ、結合次数、スピン人口、 :math:`\langle S^2\rangle` を出力します（PK積分）。

図の作成スクリプト
------------------

* :download:`plot_article_figures.py <scripts/plot_article_figures.py>` : 下記のCSVから記事中の図をすべて作成します。Psi4の計算は行いません。

数値データ（CSV）
-----------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - ファイル
     - 内容
   * - :download:`rhf_orbitals.csv <data/rhf_orbitals.csv>`
     - RHFの軌道エネルギー、擬似波数、占有数（ :math:`N` = 2–64、DF）
   * - :download:`pbe_core_orbitals.csv <data/pbe_core_orbitals.csv>`
     - RKS-PBEの同上（ :math:`N` = 2–32、コアハミルトニアン初期推定、DF）
   * - :download:`pbe_sad_orbitals.csv <data/pbe_sad_orbitals.csv>`
     - RKS-PBEの同上（ :math:`N` = 32, 48, 64、SAD初期推定、DF）
   * - :download:`rhf_pbe_comparison.csv <data/rhf_pbe_comparison.csv>`
     - 上の3ファイルから抜き出したHOMO、LUMO、軌道ギャップ
   * - :download:`hydrogen_chain_bond_order.csv <data/hydrogen_chain_bond_order.csv>`
     - RHFとRKS-PBEの隣接原子間Löwdin結合次数（ :math:`N` = 16, 32, 64、PK）。原子番号は0始まり
   * - :download:`hydrogen_chain_spin_summary.csv <data/hydrogen_chain_spin_summary.csv>`
     - 4手法の全エネルギー、軌道ギャップ、中央の交替振幅、スピン人口、 :math:`\langle S^2\rangle` （ :math:`N` = 16, 32、PK）
   * - :download:`hydrogen_chain_spin_sites.csv <data/hydrogen_chain_spin_sites.csv>`
     - 4手法の原子ごとのLöwdin電子数とスピン人口。原子番号は1始まり
   * - :download:`hydrogen_chain_spin_bonds.csv <data/hydrogen_chain_spin_bonds.csv>`
     - 4手法の隣接原子間Löwdin結合次数。原子番号は1始まり

軌道エネルギーの単位はeV、全エネルギーの単位はHartree（ :math:`E_\mathrm{h}` ）です。

計算手順
========

以下のコマンドは、Psi4 1.10の環境で、スクリプトを置いたディレクトリから実行します。各スクリプトはPsi4のログ（ ``*_psi4.log`` ）も出力します。

1. RHFの原子数依存性
--------------------

.. code-block:: bash

   python hydrogen_chain_psi4.py --method rhf --a 1.8 --ns 2 4 8 16 24 32 48 64 80 100 --prefix rhf

``rhf_orbitals.csv`` が得られます。CSVには収束した系だけが書き出されます。この条件では :math:`N` = 80, 100が500反復以内に収束せず、結果から除外されました。

2. RKS-PBEの原子数依存性
------------------------

.. code-block:: bash

   python hydrogen_chain_psi4.py --method rks --xc pbe --a 1.8 --ns 2 4 8 16 24 32 --prefix pbe_core

:math:`N` = 48, 64では、初期推定をSADに変えて計算しました。 ``hydrogen_chain_psi4.py`` の ``set_options`` にある ``'guess': 'core'`` を ``'guess': 'sad'`` に書き換えたコピー（ここでは ``pbe_sad_input.py`` とします）を使います。

.. code-block:: bash

   python pbe_sad_input.py --method rks --xc pbe --a 1.8 --ns 32 48 64 --prefix pbe_sad

コアハミルトニアン初期推定では、 :math:`N` = 64が500反復以内に収束しませんでした。 :math:`N` = 32では2つの初期推定のギャップが表示桁数で一致し、図と表にはコアハミルトニアン初期推定の結果を使っています。

3. 結合次数とRHFの安定性解析
----------------------------

.. code-block:: bash

   python hydrogen_chain_bond_order.py --a 1.8 --ns 16 32 64

``hydrogen_chain_bond_order.csv`` が得られます。Psi4 1.10の安定性解析は密度フィッティングのSCFに対応していないため、このスクリプトはPK積分を使います。RHF→RHFとRHF→UHFの安定性固有値は、ログの ``Lowest singlet (RHF->RHF) stability eigenvalues`` と ``Lowest triplet (RHF->UHF) stability eigenvalues`` に出力されます。

4. スピン制限解と非制限解の比較
------------------------------------

.. code-block:: bash

   python hydrogen_chain_spin.py --ns 16 32

``hydrogen_chain_spin_summary.csv`` 、 ``_sites.csv`` 、 ``_bonds.csv`` 、 ``_orbitals.csv`` （α・β軌道のエネルギー）が得られます。

非制限計算の初期軌道は次のようにつくります。まず同じ手法の制限解（RHFまたはRKS-PBE）のFock行列またはKohn–Sham行列をLöwdin直交化し、対角成分に :math:`\pm 0.5\ E_\mathrm{h}` の交互の場をαとβで逆符号に加えて対角化します。得られた軌道をPsi4の ``restart_file`` として読み込ませます。この場は初期軌道の生成だけに使い、SCF本計算には加えていません。ログに ``Reading orbitals`` が出力されていることで、初期軌道の読み込みを確認できます。単純なHOMO–LUMO混合による初期推定では、 :math:`N` = 16のUHFが500反復以内に収束しませんでした。

5. 図の作成
-----------

.. code-block:: bash

   python plot_article_figures.py

``scripts/`` と同じ階層の ``data/`` にあるCSVを読み、 ``figures/`` に記事中の図を出力します。あわせて、中央の結合次数の交替振幅を表示します。

数値を扱う上での注意
====================

* 原子数依存性（手順1・2）はDF-SCF、結合次数とスピンの比較（手順3・4）はPK積分で計算しています。同じ :math:`N` でも、軌道ギャップは末尾の桁（0.003 eV以下）で一致しません。例えば :math:`N` = 64のRHFギャップはDFで4.764 eV、PKで4.762 eVです。
* 中央の交替振幅は、鎖中央の8本の結合を1本おきの2組に分け、2組の平均値の差の絶対値を2で割った値です。
* 非制限計算の軌道ギャップは、両スピンを通じた最高被占有軌道と最低空軌道の差です。スピンごとのギャップも ``hydrogen_chain_spin_summary.csv`` に記録しています。
* :math:`\langle S^2\rangle` は密度行列から計算した一行列式に対する値で、Psi4のログの値と照合しました。UKSではKohn–Sham行列式の診断値として扱います。
* SCFが収束しても、得られた解が唯一の解や大域的な最低エネルギー解であることは保証されません。
* 擬似波数 :math:`ka = j\pi/(N+1)` はエネルギー順の軌道番号から割り当てたもので、周期系のk点計算や、軌道係数から求めた波数ではありません。
