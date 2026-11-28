.. _li3po4:

Li₃PO₄の構造とLiイオン拡散
==========================

非晶質Li₃PO₄では、周囲の原子配置によってLiイオンの移動しやすさが変わります。\
この連載では、Quloudで **Liが移動する経路とその障壁** を求め、**拡散係数の温度依存性** を調べます。\
まず結晶を溶融・急冷して不規則な原子配置を作り、次にLiを1個取り除いた小さなモデルと、薄膜の組成に近い大規模モデルで拡散を調べます。

* :numref:`{number}. {name} <li3po4-doc-introduction>`

  空孔の移動とLiイオンの拡散の関係を確認し、各計算で文献と何を比較するかを整理します。

.. rubric:: 結晶・非晶質の構造
   :heading-level: 2

* :numref:`{number}. {name} <li3po4-doc-beta-gamma-comparison>`

  Li₃PO₄のβ相とγ相について、計算した格子定数と体積を文献の計算値・実験値と比較します。

* :numref:`{number}. {name} <li3po4-doc-melt-quench-structure>`

  γ相のLi₃PO₄を第一原理分子動力学で溶融・急冷し、原子座標を緩和した後の構造を調べます。

.. rubric:: 空孔と移動障壁
   :heading-level: 2

* :numref:`{number}. {name} <li3po4-doc-vacancy-formation>`

  Liを取り除くサイトを変え、OpenMXと3つの機械学習原子間ポテンシャルによる空孔形成エネルギーを比較します。

* :numref:`{number}. {name} <li3po4-doc-vacancy-paths>`

  隣のLiが空孔に移る経路の形とつながりを、3つの機械学習原子間ポテンシャルで比較します。

* :numref:`{number}. {name} <li3po4-doc-vacancy-barriers>`

  各経路の順・逆方向の移動障壁を求め、モデルごとの障壁の分布を比較します。

.. rubric:: 拡散と高温の局所構造
   :heading-level: 2

* :numref:`{number}. {name} <li3po4-doc-lithium-msd>`

  Li空孔を含むモデルでLiの平均二乗変位の時間変化を計算し、温度による違いを比較します。

* :numref:`{number}. {name} <li3po4-doc-diffusivity-temperature>`

  Li空孔を含むモデルで拡散係数の温度依存性を計算し、活性化エネルギーを求めて文献値と比較します。

* :numref:`{number}. {name} <li3po4-doc-partial-rdf>`

  異なる温度で得た分子動力学の軌跡から原子対ごとの動径分布関数を求め、局所構造の温度変化を調べます。

.. rubric:: 大規模モデル
   :heading-level: 2

* :numref:`{number}. {name} <li3po4-doc-large-structure-rdf>`

  大規模なLi₃PO₄構造を分子動力学で作り、部分動径分布関数から局所的な原子配置をモデルサイズごとに比較します。

* :numref:`{number}. {name} <li3po4-doc-large-model-diffusivity>`

  1006原子モデルで拡散の活性化エネルギーを求め、同じ組成の文献計算と実験の値を比べます。

.. toctree::
   :titlesonly:
   :hidden:

   introduction
   beta-gamma-comparison
   melt-quench-structure
   vacancy-formation
   vacancy-paths
   vacancy-barriers
   lithium-msd
   diffusivity-temperature
   partial-rdf
   large-structure-rdf
   large-model-diffusivity
