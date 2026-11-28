BaTiO₃の安定構造と相転移
========================

BaTiO₃は低温では菱面体晶で、温度を上げると斜方晶、正方晶、立方晶の順に変化します。\
この連載では、Quloudで **0 Kで最も安定な構造** と **温度を上げたときの相の変化** を調べます。\
格子と原子座標を最適化し、Tiの変位に伴うエネルギー変化を調べた後、分子動力学で昇温時の構造を追います。

* :numref:`{number}. {name} <batio3-doc-introduction>`

  4つの結晶相と分極の向きを確認し、静的計算と昇温計算でそれぞれ何が分かるかを整理します。

.. rubric:: 結晶構造と相の安定性
   :heading-level: 2

* :numref:`{number}. {name} <batio3-doc-lattice-constant>`

  4つの結晶相の格子定数を可変セル最適化で求め、実験値からのずれを手法ごとに比較します。

* :numref:`{number}. {name} <batio3-doc-stability>`

  4相のエネルギーを0 Kで比較し、各手法が菱面体晶を最安定と予測するかを確かめます。

* :numref:`{number}. {name} <batio3-doc-geometry-optimization>`

  正方晶の格子を固定して原子座標を緩和し、TiとOの相対変位を手法ごとに比較します。

.. rubric:: 極性変位と相転移
   :heading-level: 2

* :numref:`{number}. {name} <batio3-doc-total-energy-dft-mlip>`

  立方晶中のTiだけを中心からずらし、エネルギーの極小がどこに現れるかを調べます。

* :numref:`{number}. {name} <batio3-doc-total-energy>`

  Ba・Ti・Oの協同変位を取り入れ、井戸の深さに対するひずみ・圧縮の影響と、Ti–O結合の電子状態を調べます。

* :numref:`{number}. {name} <batio3-doc-phase-transition>`

  昇温時のTiの局所変位と格子定数から相を判定し、3つの機械学習モデルで相の順序と転移温度を比較します。

.. toctree::
   :titlesonly:
   :hidden:

   introduction
   lattice-constant
   stability
   geometry-optimization
   total-energy-DFT-MLIP
   total-energy
   phase_transition
