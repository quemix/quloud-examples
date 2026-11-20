BaTiO₃の安定構造と相転移
========================

BaTiO₃の結晶構造と相の安定性を調べ、極性変位と有限温度での構造相転移を計算します。

* :doc:`導入 <introduction>`

  BaTiO₃の強誘電性と温度による結晶構造の変化を概観し、各計算で調べる項目を整理します。

.. rubric:: 結晶構造と相の安定性
   :heading-level: 2

* :doc:`格子定数 <lattice-constant>`

  可変セル最適化でBaTiO₃の各強誘電相の格子定数を求め、実験値と比較します。

* :doc:`安定基底状態 <stability>`

  BaTiO₃の4つの結晶相について、0 Kでの相対エネルギーを計算し、安定性の順序を比較します。

* :doc:`構造最適化 <geometry-optimization>`

  正方晶BaTiO₃の格子を固定して原子座標を緩和し、DFTと機械学習ポテンシャルの結果を比較します。

.. rubric:: 極性変位と相転移
   :heading-level: 2

* :doc:`二重井戸ポテンシャル Part 1 <total-energy-DFT-MLIP>`

  立方晶中のTi原子だけを変位させ、DFTと複数の機械学習原子間ポテンシャルでエネルギー曲線を比較します。

* :doc:`二重井戸ポテンシャル Part 2 <total-energy>`

  Ba・Ti・Oを協同的に変位させ、強誘電的不安定性の構造的・電子的な起源を調べます。

* :doc:`構造相転移 <phase_transition>`

  BaTiO₃を昇温する分子動力学計算を行い、Tiの局所変位と格子定数から相転移を調べます。

.. toctree::
   :titlesonly:
   :hidden:

   導入 <introduction>
   格子定数 <lattice-constant>
   安定基底状態 <stability>
   構造最適化 <geometry-optimization>
   二重井戸ポテンシャル Part 1 <total-energy-DFT-MLIP>
   二重井戸ポテンシャル Part 2 <total-energy>
   構造相転移 <phase_transition>
