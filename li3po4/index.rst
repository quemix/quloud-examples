.. _li3po4:

Li₃PO₄の構造とLiイオン拡散
==========================

Li₃PO₄の結晶・非晶質の構造と、Liイオンが移動する経路や速さを調べます。

* :doc:`導入 <introduction>`

  固体電解質Li₃PO₄の構造とLiイオンの拡散を扱った文献を紹介し、追試で比較する項目を整理します。

.. rubric:: 結晶・非晶質の構造
   :heading-level: 2

* :doc:`β相・γ相の結晶構造 <beta-gamma-comparison>`

  Li₃PO₄のβ相とγ相について、計算した格子定数と体積を文献の計算値・実験値と比較します。

* :doc:`溶融・急冷後の構造 <melt-quench-structure>`

  γ相のLi₃PO₄を第一原理分子動力学で溶融・急冷し、原子座標を緩和した後の構造を調べます。

.. rubric:: 空孔と移動障壁
   :heading-level: 2

* :doc:`Li空孔形成エネルギー <vacancy-formation>`

  Liを取り除くサイトを変え、OpenMXと3種の機械学習ポテンシャルによる空孔形成エネルギーを比較します。

* :doc:`Li空孔の拡散経路 <vacancy-paths>`

  Liサイトを結ぶ移動経路の形状とつながりを、3種の機械学習原子間ポテンシャルで比較します。

* :doc:`Li空孔移動障壁 <vacancy-barriers>`

  各経路の順・逆方向の移動障壁を求め、モデルごとの障壁の分布を比較します。

.. rubric:: 拡散と高温の局所構造
   :heading-level: 2

* :doc:`拡散係数の温度依存性 <diffusivity-temperature>`

  Li空孔を含むモデルで拡散係数の温度依存性を計算し、活性化エネルギーを求めて文献値と比較します。

* :doc:`Liの平均二乗変位 <lithium-msd>`

  Li空孔を含むモデルでLiの平均二乗変位の時間変化を計算し、温度による違いを比較します。

* :doc:`MD軌跡の部分RDF <partial-rdf>`

  異なる温度で得た分子動力学の軌跡から原子対ごとの動径分布関数を求め、局所構造の温度変化を調べます。

.. rubric:: 大規模モデル
   :heading-level: 2

* :doc:`大規模構造とRDF <large-structure-rdf>`

  大規模なLi₃PO₄構造を分子動力学で作り、部分動径分布関数から局所的な原子配置をモデルサイズごとに比較します。

* :doc:`大規模モデルのLi拡散係数 <large-model-diffusivity>`

  大規模なLi₃PO₄モデルをCHGNetで計算し、Liイオンの拡散係数が温度でどう変わるかを調べます。

.. toctree::
   :titlesonly:
   :hidden:

   導入 <introduction>
   β相・γ相の結晶構造 <beta-gamma-comparison>
   溶融・急冷後の構造 <melt-quench-structure>
   Li空孔形成エネルギー <vacancy-formation>
   Li空孔の拡散経路 <vacancy-paths>
   Li空孔移動障壁 <vacancy-barriers>
   拡散係数の温度依存性 <diffusivity-temperature>
   Liの平均二乗変位 <lithium-msd>
   MD軌跡の部分RDF <partial-rdf>
   大規模構造とRDF <large-structure-rdf>
   大規模モデルのLi拡散係数 <large-model-diffusivity>
