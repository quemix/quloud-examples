.. _batio3-doc-introduction:

=======================================
導入
=======================================

BaTiO₃（チタン酸バリウム）は、温度によって結晶構造と分極の向きが変わります。
この連載では Quloud を使い、どの構造が 0 K で最も安定か、昇温するとその構造がどう変わるかを調べます。

温度と分極の向き
----------------

BaTiO₃ の平均構造は、低温から順に **菱面体晶（R）→ 斜方晶（O）→ 正方晶（T）→ 立方晶（C）** と変わります。
分極の向きは、擬立方晶の軸で菱面体晶が :math:`\langle 111\rangle`、斜方晶が :math:`\langle 110\rangle`、正方晶が :math:`\langle 100\rangle` です。
室温では通常、正方晶相にあります。
約 393 K のキュリー温度を超えると、平均構造は常誘電の立方晶となります。
4 相の空間群と分極の向きは技術ノートの\ `4つの相と分極の向き <https://technical-notes.quemix.com/solid/ferroelectricity.html#batio3-four-phases>`__\ に、擬立方晶の軸の取り方は\ `ペロブスカイトの擬立方格子 <https://technical-notes.quemix.com/solid/unitcell_transform.html#pseudocubic-cell>`__\ にまとめました。

高温の立方晶相でも、瞬間的には Ti が酸素八面体の中心からずれることがあります（技術ノートの\ `局所的なTiの変位と平均構造 <https://technical-notes.quemix.com/solid/ferroelectricity.html#fe-local-average>`__）。
昇温計算では、局所変位と平均構造の両方を調べます。

BaTiO₃ は代表的なペロブスカイト型強誘電体で、誘電体、センサー、アクチュエーターなどに使われます。
強誘電体は外部電場がなくても\ `自発分極 <https://technical-notes.quemix.com/solid/ferroelectricity.html#spontaneous-polarization>`__\ をもち、電場によってその向きを反転できます。
BaTiO₃ の分極には、Ti と O が相対的にずれる\ `極性ソフトモード <https://technical-notes.quemix.com/solid/soft_mode.html#polar-soft-mode>`__、Ti–O 結合での\ `軌道の混成 <https://technical-notes.quemix.com/solid/ferroelectric_origin.html#fo-hybridization>`__、格子のひずみが関わります。

計算で調べること
----------------

* :doc:`格子定数 <lattice-constant>` と :doc:`安定基底状態 <stability>` では、4 相の格子定数と 0 K での相対エネルギーを求めます。
  :doc:`構造最適化 <geometry-optimization>` では、正方晶の格子を固定し、原子を緩和して Ti と O の相対変位を比較します。
* :doc:`二重井戸ポテンシャル Part 1 <total-energy-DFT-MLIP>` と :doc:`Part 2 <total-energy>` では、原子をずらすとエネルギーがどれだけ下がるかを調べます。
  Part 1 では Ti だけを動かし、Part 2 では Ba・Ti・O の協同変位と格子ひずみ・体積の影響を調べます。
* :doc:`構造相転移 <phase_transition>` では、分子動力学（MD）で温度を上げ、Ti の局所変位と格子定数から相の変化を追います。

0 K の全エネルギーは各構造の相対安定性を比べる基準になります。
有限温度でどの相が安定かを熱力学的に決めるには、温度ごとの\ `自由エネルギー <https://technical-notes.quemix.com/thermo/gibbs_energy.html>`__\ が必要になります。
機械学習原子間ポテンシャル（MLIP）の結果は、学習データの適用範囲を踏まえ、密度汎関数理論（DFT）の結果との差を確認して解釈します。
MLIP の仕組みと検証の観点は技術ノートの\ `機械学習原子間ポテンシャル <https://technical-notes.quemix.com/md/mlip.html>`__\ で説明しています。

